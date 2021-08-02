class WiFiNEProcessor:
    def __init__(self, annotation_path, output_path):
        self.annotation_path = annotation_path
        self.document_path = None
        self.output_path = output_path

        self.document_vocab = {}
        self.figer_vocab = {}
        self.segments = []
        self.sentences = []

        self.art_id = None
        self.sen_idx_min = None
        self.sen_idx_max = None

        self.load_document_vocab()
        self.load_figer_vocab()


    def load_document_vocab(self):
        print("BEGIN load_document_vocab()")
        path = '../document.vocab'
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                line = line.split()
                word = line[0]; index = i
                self.document_vocab[index] = word
        print("FINISH load_document_vocab()")


    def load_figer_vocab(self):
        print("BEGIN load_figer_vocab()")
        path = '../figer.vocab'
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                line = line.split()
                entity = line[0]; index = i
                self.figer_vocab[index] = entity
        print("FINISH load_figer_vocab()")


    def load_document_path(self):
        print('BEGIN load_document_path()')
        search_path = '../Documents/'
        i = 0
        while True:
            try:
                with open(search_path + str(i), 'r') as file:
                    for line in file:
                        line = line.split()
                        if line[0] == 'ID':
                            print(line[1])
                            if int(line[1]) == self.art_id:
                                self.document_path = search_path + str(i)
                                return
            except:
                pass
            i += 1
        print('FINISH load_document_path()')


    def generate(self):
        """
        Input: Path of Wilipedia article
        Result: Generate a dataset in text file format similar to CoNLL-2003
        format: [sentIdx, begin, end, menType, figer_types, gillick_types]
        """
        print('BEGIN generate()')
        print('reading figer annotations...')
        with open(self.annotation_path, 'r') as file:
            not_first = False
            for line in file:
                line = line.split()
                if (line[0] == 'ID'):
                    if not_first: # only parse the first article
                        break
                    self.art_id = int(line[1])
                    not_first = True
                    continue
                sen_idx = int(line[0]); begin = int(line[1]); end = int(line[2])
                figer_type = self.figer_vocab[int(line[4])]

                if self.sen_idx_min is None: self.sen_idx_min = sen_idx
                self.sen_idx_max = sen_idx

                self.segments = [[]] * (self.sen_idx_max - self.sen_idx_min + 1)
                self.segments[sen_idx].append([begin, end, figer_type])

        self.load_document_path() # find document with correct article id

        print('reading document data...')
        with open(self.document_path, 'r') as file:
            sen_idx = -1
            for i, line in enumerate(file):
                line = line.split()
                if line[0] != 'ID': sen_idx += 1
                if sen_idx >= self.sen_idx_min and sen_idx <= self.sen_idx_max:
                    self.sentences.append([])
                    for wrd_idx in line:
                        self.sentences[sen_idx].append(self.document_vocab[int(wrd_idx)])
        
        print('writing output file...')
        print(self.segments)
        with open(self.output_path, 'w') as file:
            for sen_idx in range(len(self.segments)):
                print('sen_idx is:', sen_idx)
                sentence = self.segments[sen_idx]
                for segment in sentence:
                    begin = segment[0]; end = segment[1] + 1; figer_entity = segment[2]
                    for i in range(begin, end + 1):
                        output = []
                        word = self.sentences[sen_idx][i]
                        output.append(word)
                        output.append(figer_entity)
                        file.write(' '.join(output))

        print("END generate()")

processor = WiFiNEProcessor('../FineEntity/0', './0') 
processor.generate()

# TODO (Jul 28): Figure how to search for document given article_idx