from lxml import etree


# all of the element types in dblp
all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}
my_elements = {"article", "inproceedings"}
# all of the feature types in dblp
all_features = {"address", "author", "booktitle", "cdrom", "chapter", "cite", "crossref", "editor", "ee", "isbn",
                "journal", "month", "note", "number", "pages", "publisher", "school", "series", "title", "url",
                "volume", "year"}


def context_iter(dblp_path):
    """Create a dblp data iterator of (event, element) pairs for processing"""
    return etree.iterparse(source=dblp_path, dtd_validation=True, load_dtd=True)  # required dtd


def extract_and_check_features(elem):
    attribs = {'key': elem.attrib['key']}
    for child in elem:
        if child.tag in all_features:
            if child.tag == 'year' and int(child.text) < 2015:
                return
            if child.tag == 'title' and not child.text:
                return
            if child.tag == 'title'\
                    and not (all(s in child.text.lower() for s in ['priva', 'recommend'])
                             or all(s in child.text.lower() for s in ['federated', 'recommend'])
                             or all(s in child.text.lower() for s in ['priva', 'distributed', 'recommend'])
                             or all(s in child.text.lower() for s in ['priva', 'decentralized', 'recommend'])
                             or all(s in child.text.lower() for s in ['priva', 'factorization'])):
                return
            if child.tag == 'title':
                attribs['title'] = child.text
                kws = [kw for kw in ('priva', 'recommend', 'federated', 'distributed', 'decentralized', 'factorization') if kw in child.text.lower()]
                attribs['kw'] = ', '.join(kws)
            if child.tag == 'author' and attribs.get('author'):
                attribs['author'] += ', ' + child.text
                continue
            attribs[child.tag] = child.text
    return attribs


def parse(dblp_path, save_path):
    f = open(save_path, 'w', encoding='utf8')
    counter = 0
    for _, e in context_iter(dblp_path):
        if e.tag in my_elements:
            attribs = extract_and_check_features(e)
            if not attribs:
                continue
            counter += 1
            f.write('=COLLEG.IPERTESTUALE("' + (attribs.get('ee') or '') + '"; "link")\t' + attribs.get('key') + '\t' +
                    attribs.get('kw') + '\t' + attribs.get('title') + '\t' + (attribs.get('author') or '') + '\t' +
                    (attribs.get('journal') or attribs.get('booktitle') or '') + '\t' +
                    (attribs.get('year') or '') + '\n')
            print('*** found ', counter)
    f.close()


def main():
    dblp_path = 'dataset/dblp.xml'
    save_path = 'dataset/article.json'
    try:
        context_iter(dblp_path)
        print("LOG: Successfully loaded \"{}\".".format(dblp_path))
    except IOError:
        print("ERROR: Failed to load file \"{}\". Please check your XML and DTD files.".format(dblp_path))
        exit()
    parse(dblp_path, save_path)


if __name__ == '__main__':
    main()
