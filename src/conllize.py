import sys
import time 


class WiFiNECoNLLizer:
    def __init__(self, annotation_path, output_path):
        self.annotation_path = annotation_path
        self.document_path = None
        self.output_path = output_path

        self.document_vocab = {}
        self.figer_vocab = {}
        self.art2doc = {} # will be populated by load_document_paths()

        self.load_document_vocab()
        self.load_figer_vocab()


    """
    Load document.vocab into self.document_vocab
    """
    def load_document_vocab(self):
        start = time.time()
        path = PREFIX + 'document.vocab'
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                line = line.split()
                word = line[0]; index = i
                self.document_vocab[index] = word
        print('time for load_document_vocab():', round(time.time() - start, 2), 'seconds')


    """
    Load figer.vocab into self.figer_vocab
    """
    def load_figer_vocab(self):
        start = time.time()
        path = PREFIX + 'figer.vocab'
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                line = line.split()
                entity = line[0]; index = i
                self.figer_vocab[index] = entity
        print('time for load_figer_vocab():', round(time.time() - start, 2), 'seconds')


    # """
    # Find and load the document file that contains the article with self.art_id 
    # """
    # # TODO Oct 25, 2021: This function seems to be the bottleneck (about 30s for 1000+ annotation indices)
    # def load_document_path(self):
    #     start = time.time()
    #     search_path = PREFIX + 'Documents/'
    #     i = 0
    #     while True:
    #         try:
    #             with open(search_path + str(i), 'r') as file:
    #                 for line in file:
    #                     line = line.split()
    #                     if line[0] == 'ID':
    #                         if int(line[1]) == self.art_id:
    #                             self.document_path = search_path + str(i)
    #                             print('time for load_document_path():', round(time.time() - start, 2), 'seconds')
    #                             return 
    #         except:
    #             pass
    #         i += 1


    def load_document_paths(self):
        start = time.time()
        search_path = PREFIX + 'Documents/'
        i = 0
        while i <= NUM_FILES:
            try:
                with open(search_path + str(i), 'r') as file:
                    for line in file:
                        line = line.split()
                        if line[0] == 'ID':
                            art_id = int(line[1])
                            self.art2doc[art_id] = search_path + str(i)
            except:
                pass
            i += 1
        print('time for load_document_paths():', round(time.time() - start, 2), 'seconds', '\n')


    """
    Input: Path of Wilipedia article
    Result: Generate a dataset in text file format similar to CoNLL-2003
    format: [sentIdx, begin, end, menType, figer_types, gillick_types]
    """
    def conllize_article(self, annotation_path, output_path, art_id, sen_idx_min, sen_idx_max):
        # print('annotation_path:', annotation_path)
        # print('output_path:', output_path)
        # print('art_id:', art_id)
        # print('sen_idx_min:', sen_idx_min)
        # print('sen_idx_max:', sen_idx_max)
        # if (art_id != 432236):
        #     return
        start = time.time()
        # Read figer annotations]
        segments = [None] * (sen_idx_max - sen_idx_min + 1) # don't do self.segments = [[]] * 66
        for i in range(len(segments)):
            segments[i] = []

        with open(annotation_path, 'r') as file:
            found = False
            for line in file:
                line = line.split()
                if (line[0] == 'ID'):
                    if found: 
                        break # only parse the target article (since there the article)
                    if (int(line[1]) == art_id):
                        found = True
                elif found:
                    try:
                        sen_idx = int(line[0]); begin = int(line[1]); end = int(line[2]) - 1 # it looks like the end is exclusive
                        men_type = int(line[3]); figer_type = self.figer_vocab[int(line[4])]
                        # print('sen_idx:', sen_idx)
                    except: # the line is malformed
                        print('malformed...')
                        continue
                    # self.segments[i] is a list of tuple; each tuple corresponds to a segment in sentence i
                    if men_type == 0: # means it's a named entity
                        segments[sen_idx - sen_idx_min].append([begin, end, figer_type]) # occasionally in the annotation file an article starts at sentence 1 for some reason

        document_path = self.art2doc[art_id]
        sentences = []
        # Read document data
        with open(document_path, 'r') as file:
            sen_idx = -1
            right_article = False
            for i, line in enumerate(file):
                line = line.split()
                if line[0] == 'ID':
                    if int(line[1]) == art_id: 
                        right_article = True
                        continue
                    elif right_article:
                        break
                if right_article:
                    sen_idx += 1
                    if sen_idx >= sen_idx_min and sen_idx <= sen_idx_max:
                        sentences.append([])
                        for wrd_idx in line:
                            sentences[sen_idx - sen_idx_min].append(self.document_vocab[int(wrd_idx)]) # occasionally in the annotation file an article starts at sentence 1 for some reason
        
        # Write output file
        substart = time.time()
        with open(output_path, 'a') as file:
            file.write('\n-DOCSTART-          O\n')
            for sen_idx, sentence in enumerate(sentences):
                file.write('\n')
                for word_idx, word in enumerate(sentence):
                    output = [word]
                    segments_at_sen_idx = segments[sen_idx]
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
        # print('time to write output file in conllize():', round(time.time() - substart, 2), 'seconds')
        # print('time for conllize():', round(time.time() - start, 2), 'seconds', '\n')


    def conllize_file(self, annotation_path, output_path):
        start = time.time()
        # Read figer annotations
        art_id = None
        with open(annotation_path, 'r') as file:
            for line in file:
                line = line.split()
                if (line[0] == 'ID'):
                    if art_id is not None:
                        self.conllize_article(annotation_path, output_path, art_id, sen_idx_min, sen_idx_max)
                    art_id = int(line[1])
                    sen_idx_min = None
                    sen_ind_max = None 
                else:
                    sen_idx = int(line[0])
                    if sen_idx_min is None: 
                        sen_idx_min = sen_idx
                    sen_idx_max = sen_idx
            self.conllize_article(annotation_path, output_path, art_id, sen_idx_min, sen_idx_max) # last article in a file
        print('time for conllize_file():', round(time.time() - start, 2), 'seconds', '\n')


    def conllize_all(self):
        start = time.time()
        self.load_document_paths()
        for i in range(82, 100):
            self.conllize_file(self.annotation_path + str(i), self.output_path + str(i))
        print('time for conllize_all():', round(time.time() - start, 2), 'seconds', '\n')




#### ------------------------------------------------------------
NUM_FILES = 3241
PREFIX = '../WiFiNE_original/'
annotation_path = PREFIX + 'FineEntity/'
output_path = '../WiFiNE_CoNLLized/'


# args = sys.argv[1:]
# try:
#     for i, arg in enumerate(args):
#         if arg == '-a':
#             annotation_path += args[i + 1]
#         elif arg == '-o':
#             output_path += args[i + 1]

#     conllizer = WiFiNECoNLLizer(annotation_path, output_path) 
#     if (len(args) > 0):
#         conllizer.conllize()
#     else:
#         conllizer.conllize_all()
             
# except getopt.error as err:
#     print(err)

conllizer = WiFiNECoNLLizer(annotation_path, output_path) 
conllizer.conllize_all()
