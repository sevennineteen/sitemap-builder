import codecs
import logging
from xml.sax.saxutils import escape

class Sitemap(file):

    # Sitemap protocol constraints
    xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>'
    root_open = '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    root_close = '</urlset>'
    properties = ['loc', 'lastmod', 'changefreq', 'priority']
    max_entries = 50000
    reporting_interval = 10000

    def __init__(self, path):
        self.path = path

    def open(self, mode='r', encoding='utf-8'):
        self.file = codecs.open(self.path, mode, encoding)
        logging.debug('Opened sitemap file: %s' % self.path)

    def close(self):
        self.file.close()
        logging.debug('Closed sitemap file: %s' % self.path)

    def writeline(self, content):
        self.file.write(content + '\n')

    def begin(self):
        self.open('w')
        self.writeline(self.xml_declaration)
        self.writeline(self.root_open)
        self.entries = 0
        logging.info('Started writing sitemap: %s' % self.path)

    def add_entry(self, **kwargs):
        self.writeline('  <url>')

        for p in self.properties:
            if kwargs.get(p):
                self.writeline('    <%s>%s</%s>' % (p, escape(kwargs[p]), p))
        
        self.writeline('  </url>')
        self.entries += 1
        
        logging.debug('Added entry to sitemap: %s %s' % (self.path, str(kwargs)))

        if self.entries % self.reporting_interval == 0:
            logging.info('Processed %s entries; last entry: %s' % (self.entries, str(kwargs)))

    def end(self):
        self.writeline(self.root_close)
        self.close()
        logging.info('Finished writing sitemap: %s [%s entries]' % (self.path, self.entries))

    def _get_closed(self):
        return not self.file or self.file.closed

    closed = property(_get_closed)