import codecs
import logging
import gzip
from xml.sax.saxutils import escape

class Sitemap(file):
    "Represents a Sitemap file in XML format."
    
    # Sitemap protocol constraints
    xml_schema = {'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
    root_elem = 'urlset'
    entry_elem = 'url'
    properties = ['loc', 'lastmod', 'changefreq', 'priority']
    max_entries = 50000

    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    reporting_interval = 10000

    def __init__(self, path, compress=False):
        "Instantiates the sitemap at supplied path, with optional gzip compression."
        self.path = path
        self.compress = compress

    def open(self, mode='r', encoding='utf-8'):
        "Opens the sitemap file."
        self.file = codecs.open(self.path, mode, encoding)
        logging.debug('Opened file: %s' % (self.path))

    def close(self):
        "Closes the sitemap file."
        self.file.close()
        logging.debug('Closed file: %s' % self.path)

    def writeline(self, content):
        "Writes a line into the sitemap file."
        self.file.write(content + '\n')

    def make_gzip(self):
        "Creates a GZIP-compressed version of the sitemap file."
        self.gzip_path = self.path + '.gz'
        f_in = open(self.path, 'rb')
        f_out = gzip.open(self.gzip_path, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        logging.info('Gzipped file as: %s' % self.gzip_path)

    def begin(self):
        "Begins writing the sitemap file, including XML declaration and root element."
        self.open('w')
        self.writeline(self.xml_declaration)
        self.writeline('<%s %s>' % (self.root_elem, ' '.join(
                ['%s="%s"' % (k, self.xml_schema[k]) for k in sorted(self.xml_schema.keys())]
            )))
        self.entries = 0
        logging.info('Started writing file: %s' % self.path)

    def add_entry(self, **kwargs):
        "Writes the provided entry into the sitemap file."
        self.writeline('  <%s>' % self.entry_elem)

        for p in self.properties:
            if kwargs.get(p):
                self.writeline('    <%s>%s</%s>' % (p, escape(kwargs[p]), p))
        
        self.writeline('  </%s>' % self.entry_elem)
        self.entries += 1
        
        logging.debug('Added entry: %s' % str(kwargs))

        if self.entries % self.reporting_interval == 0:
            logging.info('Processed %s entries; last entry: %s' % (self.entries, str(kwargs)))

    def end(self):
        "Finishes writing the sitemap file, and initiates GZIP-compression if appropriate."
        self.writeline('</%s>' % self.root_elem)
        self.close()
        logging.info('Finished writing file: %s [%s entries]' % (self.path, self.entries))

        if self.compress:
            self.make_gzip()

    def _get_closed(self):
        "Returns True if sitemap is closed."
        return not self.file or self.file.closed

    closed = property(_get_closed)


class SitemapIndex(Sitemap):
    "Represents a Sitemap Index file in XML format."

    # Sitemap protocol constraints
    root_elem = 'sitemapindex'
    entry_elem = 'sitemap'
    properties = ['loc', 'lastmod']
    max_entries = 50000

    reporting_interval = 100