import codecs
import logging
import gzip
from xml.sax.saxutils import escape

class Sitemap(file):

    # Sitemap protocol constraints
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    root_open = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    root_close = '</urlset>'
    properties = ['loc', 'lastmod', 'changefreq', 'priority']
    max_entries = 50000
    reporting_interval = 10000

    def __init__(self, path, compress=False):
        self.path = path
        self.compress = compress

    def open(self, mode='r', encoding='utf-8'):
        self.file = codecs.open(self.path, mode, encoding)
        logging.debug('Opened file: %s' % (self.path))

    def close(self):
        self.file.close()
        logging.debug('Closed file: %s' % self.path)

    def writeline(self, content):
        self.file.write(content + '\n')

    def make_gzip(self):
        self.gzip_path = self.path + '.gz'
        f_in = open(self.path, 'rb')
        f_out = gzip.open(self.gzip_path, 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        logging.info('Gzipped file as: %s' % self.gzip_path)

    def begin(self):
        self.open('w')
        self.writeline(self.xml_declaration)
        self.writeline(self.root_open)
        self.entries = 0
        logging.info('Started writing file: %s' % self.path)

    def add_entry(self, **kwargs):
        self.writeline('  <url>')

        for p in self.properties:
            if kwargs.get(p):
                self.writeline('    <%s>%s</%s>' % (p, escape(kwargs[p]), p))
        
        self.writeline('  </url>')
        self.entries += 1
        
        logging.debug('Added entry: %s' % str(kwargs))

        if self.entries % self.reporting_interval == 0:
            logging.info('Processed %s entries; last entry: %s' % (self.entries, str(kwargs)))

    def end(self):
        self.writeline(self.root_close)
        self.close()
        logging.info('Finished writing file: %s [%s entries]' % (self.path, self.entries))

        if self.compress:
            self.make_gzip()

    def _get_closed(self):
        return not self.file or self.file.closed

    closed = property(_get_closed)


class SitemapIndex(Sitemap):

    # Sitemap protocol constraints
    root_open = '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    root_close = '</sitemapindex>'
    properties = ['loc', 'lastmod']
    reporting_interval = 100

    def add_entry(self, **kwargs):
        self.writeline('  <sitemap>')

        for p in self.properties:
            if kwargs.get(p):
                self.writeline('    <%s>%s</%s>' % (p, escape(kwargs[p]), p))
        
        self.writeline('  </sitemap>')
        self.entries += 1
        
        logging.debug('Added entry: %s' % str(kwargs))

        if self.entries % self.reporting_interval == 0:
            logging.info('Processed %s entries; last entry: %s' % (self.entries, str(kwargs)))