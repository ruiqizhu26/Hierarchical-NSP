import sys
import time 


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
        '''
        Load document.vocab into self.document_vocab
        '''
        # print("BEGIN load_document_vocab()")
        path = '../WiFiNE_original/document.vocab'
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                line = line.split()
                word = line[0]; index = i
                self.document_vocab[index] = word
        # print("FINISH load_document_vocab()")


    def load_figer_vocab(self):
        '''
        Load figer.vocab into self.figer_vocab
        '''
        # print("BEGIN load_figer_vocab()")
        path = '../WiFiNE_original/figer.vocab'
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                line = line.split()
                entity = line[0]; index = i
                self.figer_vocab[index] = entity
        # print("FINISH load_figer_vocab()")


    def load_document_path(self):
        '''
        Find and load the document file that contains the article with self.art_id 
        '''
        # print('BEGIN load_document_path()')
        search_path = '../WiFiNE_original/Documents/'
        i = 0
        while True:
            try:
                with open(search_path + str(i), 'r') as file:
                    for line in file:
                        line = line.split()
                        if line[0] == 'ID':
                            if int(line[1]) == self.art_id:
                                self.document_path = search_path + str(i)
                                return
            except:
                pass
            i += 1
        # print('FINISH load_document_path()')


    def generate(self):
        """
        Input: Path of Wilipedia article
        Result: Generate a dataset in text file format similar to CoNLL-2003
        format: [sentIdx, begin, end, menType, figer_types, gillick_types]
        """
        start = time.time()
        # print('BEGIN generate()')
        # print('reading figer annotations...')
        with open(self.annotation_path, 'r') as file:
            not_first = False
            for line in file:
                line = line.split()
                if (line[0] == 'ID'):
                    if not_first: break # only parse the first article
                    self.art_id = int(line[1])
                    not_first = True
                    continue
                sen_idx = int(line[0])

                if self.sen_idx_min is None: self.sen_idx_min = sen_idx
                self.sen_idx_max = sen_idx

        self.segments = [None] * (self.sen_idx_max - self.sen_idx_min + 1) # Warning: do not do self.segments = [[]] * 66!
        for i in range(len(self.segments)):
            self.segments[i] = []

        with open(self.annotation_path, 'r') as file:
            not_first = False
            for line in file:
                line = line.split()
                if (line[0] == 'ID'):
                    if not_first: break # only parse the first article
                    self.art_id = int(line[1])
                    not_first = True
                    continue
                try:
                    sen_idx = int(line[0]); begin = int(line[1]); end = int(line[2]) - 1 # it looks like the end is exclusive
                    men_type = int(line[3]); figer_type = self.figer_vocab[int(line[4])]
                except: # the line is malformed
                    continue
                # self.segments[i] is a list of tuple; each tuple corresponds to a segment in sentence i
                if men_type == 0: # means it's a named entity
                    self.segments[sen_idx].append([begin, end, figer_type])

        self.load_document_path() # find document with correct article id

        # print('reading document data...')
        with open(self.document_path, 'r') as file:
            sen_idx = -1
            right_article = False
            for i, line in enumerate(file):
                line = line.split()
                if line[0] == 'ID':
                    if int(line[1]) == self.art_id: 
                        right_article = True
                        continue
                    elif right_article:
                        break
                if right_article:
                    sen_idx += 1
                    if sen_idx >= self.sen_idx_min and sen_idx <= self.sen_idx_max:
                        self.sentences.append([])
                        for wrd_idx in line:
                            self.sentences[sen_idx].append(self.document_vocab[int(wrd_idx)])
        
        # print('writing output file...')
        with open(self.output_path, 'w') as file:
            file.write('-DOCSTART-          O\n')
            for sen_idx, sentence in enumerate(self.sentences):
                file.write('\n')
                for word_idx, word in enumerate(sentence):
                    output = [word]
                    segments_at_sen_idx = self.segments[sen_idx]
                    have_ne = False
                    for segment in segments_at_sen_idx:
                        begin = segment[0]; end = segment[1]; figer_entity = segment[2]
                        if word_idx >= begin and word_idx <= end:
                            have_ne = True
                            output.append(figer_entity)
                        elif word_idx < begin: 
                            break
                    if not have_ne:
                        output.append('O')
                    sep = ''.join([' '] * (20 - len(word)))
                    file.write(sep.join(output) + '\n')
        # print("END generate()")
        print('time taken:', time.time() - start)


# Remove 1st argument from the
# list of command line arguments
args = sys.argv[1:]

annotation_path = '../WiFiNE_original/FineEntity/'
output_path = '../WiFiNE_CoNLLized/'

try:
    # Parsing argument
    for i, arg in enumerate(args):
        if arg == '-a':
            annotation_path += args[i + 1]
        elif arg == '-o':
            output_path += args[i + 1]
             
except getopt.error as err:
    # output error, and return with an error code
    print(str(err))


processor = WiFiNEProcessor(annotation_path, output_path) 
processor.generate()
