#/usr/bin/env python
# -*- coding: utf-8 -*

try:
    import xlrd
except ImportError:
    print("You must install xlrd to use yaml_generator. see ./install_depend.py")
    exit(1)

from parse_base import parse_base

# parse xlsx file config
XLSX_FRONT_GUARD_FLAG_VERSION_1 = 'PROCESS'
XLSX_FRONT_GUARD_FLAG_VERSION_2 = 'Function'

class parse_xlsx(parse_base):
    def __init__(self):
        super().__init__()
        
    @classmethod
    def parseSingleSheet(cls, sheet, parsed_info):
        info_fetch_conf_list = []
        print("parse sheet: " + sheet.name)
        
        nrows = sheet.nrows
        ncols = sheet.ncols
        for r in range(0, nrows):
            if sheet.cell(r, 0).value == XLSX_FRONT_GUARD_FLAG_VERSION_1:
                cls.parseIndexConfXlsx(sheet, r, info_fetch_conf_list)
                continue
            if len(info_fetch_conf_list) > 0:
                for single_index_conf in info_fetch_conf_list:
                    if 'K' in single_index_conf:
                        if sheet.cell(r, single_index_conf['FORMAT']).ctype == 0 or \
                           sheet.cell(r, single_index_conf['M']).ctype      == 0 or \
                           sheet.cell(r, single_index_conf['N']).ctype      == 0 or \
                           sheet.cell(r, single_index_conf['K']).ctype      == 0 or \
                           sheet.cell(r, single_index_conf['LDA']).ctype    == 0 or \
                           sheet.cell(r, single_index_conf['LDB']).ctype    == 0 or \
                           sheet.cell(r, single_index_conf['LDC']).ctype    == 0 : 
                            continue
                           
                        FORMAT   = str(sheet.cell(r, single_index_conf['FORMAT']).value)
                        M        = str(int(sheet.cell(r, single_index_conf['M']).value))
                        N        = str(int(sheet.cell(r, single_index_conf['N']).value))
                        K        = str(int(sheet.cell(r, single_index_conf['K']).value))
                        LDA      = str(int(sheet.cell(r, single_index_conf['LDA']).value))
                        LDB      = str(int(sheet.cell(r, single_index_conf['LDB']).value))
                        LDC      = str(int(sheet.cell(r, single_index_conf['LDC']).value))
                        
                        yaml_format_info = {'DGEMM': {}}
                        yaml_format_info['DGEMM']['FORMAT'] = FORMAT
                        yaml_format_info['DGEMM']['M'] = M
                        yaml_format_info['DGEMM']['N'] = N
                        yaml_format_info['DGEMM']['K'] = K
                        yaml_format_info['DGEMM']['LDA'] = LDA
                        yaml_format_info['DGEMM']['LDB'] = LDB
                        yaml_format_info['DGEMM']['LDC'] = LDC
                        yaml_format_info['DGEMM']['LDD'] = LDC
                        yaml_format_info['DGEMM']['CONTENT'] = "[ {:>5}, {:>5}, {:>5}, {:>5}, {:>5}, {:>5}, {:>5}, {:>5} ]\n".format(M, N, "1", K, LDC, LDC, LDA, LDB)
                        
                        cls.updateParseInfo(yaml_format_info, parsed_info)
                    else:
                        if sheet.cell(r, single_index_conf['FORMAT']).ctype == 0 or   \
                           sheet.cell(r, single_index_conf['M']).ctype      == 0 or   \
                           sheet.cell(r, single_index_conf['N']).ctype      == 0 or   \
                           sheet.cell(r, single_index_conf['LDA']).ctype      == 0 or \
                           sheet.cell(r, single_index_conf['LDB']).ctype      == 0 :
                            continue
                        
                        FORMAT   = str(sheet.cell(r, single_index_conf['FORMAT']).value)
                        M        = str(int(sheet.cell(r, single_index_conf['M']).value))
                        N        = str(int(sheet.cell(r, single_index_conf['N']).value))
                        LDA      = str(int(sheet.cell(r, single_index_conf['LDA']).value))
                        LDB      = str(int(sheet.cell(r, single_index_conf['LDB']).value))
                        
                        yaml_format_info = {}
                        if FORMAT == 'RLTU':
                            yaml_format_info = cls.rltu2nt(M, N, LDA, LDB)
                        elif FORMAT == 'LLNU':
                            yaml_format_info = cls.llnu2nn(M, N, LDA, LDB)
                        
                        cls.updateParseInfo(yaml_format_info, parsed_info)
                                
        print("sheet: " + sheet.name + " parse completed!")
    
    @classmethod
    def parseSingleSheetWithoutDuplicate(cls, book, tar_sheet_name):
        tar_sheet_info = {}
        history_sheet_info = {}
        
        tar_sheet = book.sheet_by_name(tar_sheet_name)
        cls.parseSingleSheet(tar_sheet, tar_sheet_info)

        for sheet in book.sheets():
            if sheet != tar_sheet:
                cls.parseSingleSheet(sheet, history_sheet_info)
        cls.makedifference(tar_sheet_info, history_sheet_info)

        return tar_sheet_info
        
    @classmethod
    def parse(cls, in_path, sheet_name = ''):
        print("parse xlsx file:" + in_path)
        
        try:
            book = xlrd.open_workbook(in_path)
        except IOError:
            print("Can't open xlsx file: " + in_path)
            exit(1)
        
        #parsed_info [function, format, m, n, k, lda, ldb, ldc]
        parsed_info = {}
        if sheet_name == '':
            sheet_num = len(book.sheets())
            sheet_idx = 1
            for sheet in book.sheets():
                print("parsing " + str(sheet_idx) + " of " + str(sheet_num) + " sheets")
                cls.parseSingleSheet(sheet, parsed_info)
        else:
            parsed_info = cls.parseSingleSheetWithoutDuplicate(book, sheet_name)
        
        print("xlsx file:" + in_path + " parse completed!")
        return parsed_info
        
    @staticmethod
    def parseIndexConfXlsx(sheet, r, info_fetch_conf_list):
        print("start parse xlsx index conf...")
        ncols = sheet.ncols
        
        index_conf = {}
        for c in range(0, ncols):
            if sheet.cell(r, c).ctype == 0:
                if len(index_conf) > 0:
                    info_fetch_conf_list.append(index_conf)
                    index_conf = {}
            else:
                index_conf[str(sheet.cell(r, c).value).upper()] = c
        
        if len(index_conf) > 0:
            info_fetch_conf_list.append(index_conf)
        
        print("parse index conf completed!   Info as follows:")
        for index in info_fetch_conf_list:
            print(index)