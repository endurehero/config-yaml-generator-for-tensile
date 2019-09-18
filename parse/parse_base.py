#/usr/bin/env python
# -*- coding: utf-8 -*

'''
parsed_info struct:
dict:
format
NT    -> M -> N -> K -> LDA -> LDB -> LDC -> YAML_EXACT_INFO
NN    -> the same to up.
----------------------------
RLTU  -> M -> N -> LDA -> LDB -> EXACT -> YAML_EXACT_INFO
                                 RANGE -> YAML_RANGE_INFO
LLNU  -> the same to up.
'''

class parse_base():
    def __init__(self):
        pass
    
    @classmethod
    def parse(cls, in_path):
        pass
    
    # if the config should be delete , return true, otherwise, return false
    @staticmethod
    def isDeleteDGEMM(FORMAT, M, N, K, LDA, LDB, LDC, parse_info):
        
        int_m = int(M)
        int_n = int(N)
        int_k = int(K)
        int_lda = int(LDA)
        int_ldb = int(LDB)
        int_ldc = int(LDC)
        # rule1 : when m,n in [0,1], conf should be delete.
        if int_m == 0 or int_n == 0:
            return True
        if int_m == 1 or int_n == 1:
            return True
        
        # rule2 : if NT  lda < M or ldb < N or ldc < M, the conf should be deleted.
        if FORMAT == 'NT':
            if int_lda < int_m or int_ldb < int_n or int_ldc < int_m:
                return True
        # rule3 : if NN lda < M or ldb < K or ldc < M
        if FORMAT == 'NN':
            if int_lda < int_m or int_ldb < int_k or int_ldc < int_m:
                return True
                
        # rule4 : if lda is not the largerest when m, n, k are the same, the conf should be deleted.
        if M in parse_info:
            if N in parse_info[M]:
                if K in parse_info[M][N]:
                    int_lda = int(parse_info[M][N][K].keys()[0])
                    if int_lda < int(LDA):
                        return False
                    else:
                        return True

        return False
        
# if the config should be delete , return true, otherwise, return false
    @staticmethod
    def isDeleteTRSM(FORMAT, M, N,LDA, LDB, parse_info):
    
        int_m = int(M)
        int_n = int(N)
        int_lda = int(LDA)
        int_ldb = int(LDB)
        
        # rule1 : if any of m, n, lda, ldb == 0, the conf should be deleted
        if int_m == 0 or int_n == 0 or int_lda == 0 or int_ldb == 0:
            return True
            
        # rule2 : if m == 1 or n == 1 or lda == 1 or ldb == 1, the conf should be deleted
        if int_m == 1 or int_n == 1 or int_lda == 1 or int_ldb == 1:
            return True
        
        # rule3 : if FORMAT, M , N, LDA, LDB, LDC already exits, the conf should be deleted.
        if FORMAT in parse_info:
            if M in parse_info[FORMAT]:
                if N in parse_info[FORMAT][M]:
                    if LDA in parse_info[FORMAT][M][N]:
                        if LDB in parse_info[FORMAT][M][N][LDA]:
                            return True
        return False
        
#    NT: (for RLTU)
#        1)	M: # of right hand sides (a number in the range 0-45 000)   N: 128 K: 128  alpha: 1   beta: 0   lda/ldc/ldd = trsm ldb, ldb=128
#
#        Calling info:     (# Rows B/128) calls     (e.g # Rows = 384 : 3 calls, # Rows = 512 : 4 calls, etc.) * This is the only size that gets called multiple times 
#
#        2)	M: # of right hand sides (a number in the range 0-45 000)  N: 128 K: (128, 256, 384, … , # Rows of B - 128) lda/ldc/ldd = trsm ldb, ldb= trsm lda
#
#        Calling info:  Many calls with different Ks   (e.g # Rows = 256 : 1 call with K of 128 #Rows = 512 : 3 calls with K values of 128, 256, 384, etc.)

    @staticmethod
    def rltu2nt(M, N, lda, ldb):
        yaml_format_info = {}
        
        #1 generate type1 degemm
        if lda != '128':
            yaml_format_info['DGEMM'] = {}
            yaml_format_info['DGEMM']['FORMAT'] = 'NT'
            yaml_format_info['DGEMM']['M'] = M
            yaml_format_info['DGEMM']['N'] = "128"
            yaml_format_info['DGEMM']['K'] = N
            yaml_format_info['DGEMM']['LDA'] = ldb
            yaml_format_info['DGEMM']['LDB'] = lda
            yaml_format_info['DGEMM']['LDC'] = ldb
            yaml_format_info['DGEMM']['LDD'] = ldb
            yaml_format_info['DGEMM']['CONTENT'] = "[ {:>5}, {:>5}, {:>5}, {:>5}, {:>5}, {:>5}, {:>5}, {:>5} ]\n".format(M, "128", "1", N, ldb, ldb, ldb, "128")
        
        #2 generate type2 dgemm
        largest_ks = int(N) - 128
        if largest_ks >= 128:
            yaml_format_info['TRSM'] = {}
            yaml_format_info['TRSM']['FORMAT'] = 'RLTU'
            yaml_format_info['TRSM']['M'] = M
            yaml_format_info['TRSM']['N'] = N
            yaml_format_info['TRSM']['LDA'] = lda
            yaml_format_info['TRSM']['LDB'] = ldb
            yaml_format_info['TRSM']['CONTENT'] = "[ [{:>5}], [{:>5}], [{:>5}], [ {:>5}, {:>5}, {:>5} ], [{:>5}], [{:>5}], [{:>5}], [{:>5}] ]\n".format(M, "128", "1", "128", "128", str(int(N) - 128), ldb, ldb, ldb, lda)
            
        return yaml_format_info


#    NN: (for LLNU)
#        1)	M and N are swapped - lda/ldb = 128 ldc= trsm ldb
#
#        2)	M and N are swapped – lda = trsm lda, ldb/ldc = trsm ldb, ldd= 128

    @staticmethod
    def llnu2nn(M, N, lda, ldb):
        pass
    
    #parse_info:[FORMAT:[M:[N:[K:[LDA:[LDB:[LDC:[yaml_str]]]]]]]]
    @classmethod
    def updateParseInfo(cls, yaml_format_info, parsed_info):
        if 'DGEMM' in yaml_format_info:
            format = yaml_format_info['DGEMM']['FORMAT']
            m      = yaml_format_info['DGEMM']['M']
            n      = yaml_format_info['DGEMM']['N']
            k      = yaml_format_info['DGEMM']['K']
            lda    = yaml_format_info['DGEMM']['LDA']
            ldb    = yaml_format_info['DGEMM']['LDB']
            ldc    = yaml_format_info['DGEMM']['LDC']
            ldd    = yaml_format_info['DGEMM']['LDD']
            content = yaml_format_info['DGEMM']['CONTENT']
            if not cls.isDeleteDGEMM(format, m, n, k, lda, ldb, ldc, parsed_info):
                # determine whether there is duplication
                if not format in parsed_info:
                    parsed_info[format] = {}
                if not m in parsed_info[format]:
                    parsed_info[format][m] = {}
                if not n in parsed_info[format][m]:
                    parsed_info[format][m][n] = {}
                if not k in parsed_info[format][m][n]:
                    parsed_info[format][m][n][k] = {}
                    
                if len(parsed_info[format][m][n][k]) > 0:
                    parsed_info[format][m][n][k] = {}
                
                if not lda in parsed_info[format][m][n][k]:
                    parsed_info[format][m][n][k][lda] = {}
                if not ldb in parsed_info[format][m][n][k][lda]:
                    parsed_info[format][m][n][k][lda][ldb] = {}
                if not ldc in parsed_info[format][m][n][k][lda][ldb]:
                    parsed_info[format][m][n][k][lda][ldb][ldc] = {}
                if not ldd in parsed_info[format][m][n][k][lda][ldb][ldc]:
                    parsed_info[format][m][n][k][lda][ldb][ldc][ldd] = {}
                    # M N batch K LDD LDC LDA LDB
                    parsed_info[format][m][n][k][lda][ldb][ldc][ldd]['CONTENT'] = content
        if 'TRSM' in yaml_format_info:
            format = yaml_format_info['TRSM']['FORMAT']
            m      = yaml_format_info['TRSM']['M']
            n      = yaml_format_info['TRSM']['N']
            lda    = yaml_format_info['TRSM']['LDA']
            ldb    = yaml_format_info['TRSM']['LDB']
            content = yaml_format_info['TRSM']['CONTENT']
            
            if not cls.isDeleteTRSM(format, m, n, lda, ldb, parsed_info):
                if not format in parsed_info:
                    parsed_info[format] = {}
                if not m in parsed_info[format]:
                    parsed_info[format][m] = {}
                if not n in parsed_info[format][m]:
                    parsed_info[format][m][n] = {}
                if not lda in parsed_info[format][m][n]:
                    parsed_info[format][m][n][lda] = {}
                if not ldb in parsed_info[format][m][n][lda]:
                    parsed_info[format][m][n][lda][ldb] = {}
                    parsed_info[format][m][n][lda][ldb]['CONTENT'] = content

    @classmethod
    def makedifference(cls, a, b):
        remove_list = []
        for format in a:
            if format in b:
                if cls.removeDuplicateItem(a, b, format):
                    remove_list.append(format)
        
        for format in remove_list:
            a.pop(format)

    @classmethod
    def removeDuplicateItem(cls, a, b, key):
        if 'CONTENT' == key:
            return True

        remove_list = []
        for new_key in a[key]:
            if new_key in b[key]:
                if cls.removeDuplicateItem(a[key], b[key], new_key):
                    remove_list.append(new_key)
        for remove_key in remove_list:
            a[key].pop(remove_key)

        if 0 == len(a[key]):
            return True
        else:
            return False
            
    
            
        