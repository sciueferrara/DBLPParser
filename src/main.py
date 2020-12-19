from lxml import etree


# all of the element types in dblp
all_elements = {"article", "inproceedings", "proceedings", "book", "incollection", "phdthesis", "mastersthesis", "www"}
my_elements = {"article", "inproceedings", "phdthesis"}
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
            if child.tag == 'year' and int(child.text) < 2000:
                return
            if child.tag == 'name'\
                    and not (all(s in child.text for s in ['priva', 'recommend'])
                             or all(s in child.text for s in ['federate', 'recommend'])):
                return
            if child.tag == 'author' and attribs.get('author'):
                attribs['author'] = attribs['author'] + ', ' + child.text
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
            f.write('<a href="' + attribs.get('ee') + '">link</a>\t' + attribs.get('key') + '\t' +
                    attribs.get('author') + '\t' +
                    (attribs.get('journal') or attribs.get('booktitle') or '') + '\t' +
                    attribs.get('year') + '\n')
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
