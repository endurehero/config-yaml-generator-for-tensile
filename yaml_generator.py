#/usr/bin/env python
# -*- coding: utf-8 -*
import sys
import os

try:
    import gflags
except ImportError:
    print("You must install gflags to use yaml_generator. see install_depend.sh")
    exit(1)

from parse.parse_xlsx import parse_xlsx

import template.template_dgemm_nt_inc_asm_full as dgemm_nt_inc
import template.template_dgemm_nn_inc_asm_full as dgemm_nn_inc


#define input args
gflags.DEFINE_string('input_file', '', 'new kernel size file')
gflags.DEFINE_string('sheet_name', '', 'specify the sheet name when input is a xlsx file, default: process all of sheets')
gflags.DEFINE_string('output_folder', '.', 'output path, default is current folder')
gflags.DEFINE_integer('dgemm_nt_inc_start_idx', 0, 'specify the start_idx of dgemm_nt_inc yaml, default is 0')
gflags.DEFINE_integer('dgemm_nn_inc_start_idx', 0, 'specify the start idx of dgemm nn inc yaml, default is 0')

def saveYamlFile(contents, out_path):

    path = os.path.split(out_path)[0]
    if not os.path.exists(path):
        os.mkdir(path)

    try:
        f = open(out_path, 'w')
    except IOError:
        print("Can't open file: {}".format(out_path))
        exit(1)
    
    f.write(contents)
    f.close()

# input: 
# NT, M, N, K, LDA, LDB, LDC, LDD
# RLTU, M, N, LDA, LDB
def generateNT(nt_parse_info):
    dict = {}
    file_idx = gflags.FLAGS.dgemm_nt_inc_start_idx
    
    rltu_content = ''
    if 'RLTU' in nt_parse_info:
        dict_parsed_info = nt_parse_info['RLTU']
        for M in dict_parsed_info:
            for N in dict_parsed_info[M]:
                for LDA in dict_parsed_info[M][N]:
                    for LDB in dict_parsed_info[M][N][LDA]:
                        rltu_content += '          - Range: '
                        rltu_content += dict_parsed_info[M][N][LDA][LDB]['CONTENT']
                        
    if 'NT' in nt_parse_info:
        dict_parsed_info = nt_parse_info['NT']
        for M in dict_parsed_info:
            for N in dict_parsed_info[M]:
                for K in dict_parsed_info[M][N]:
                    if not K in dict:
                        dict[K] = {}
                        dict[K]['file_name'] = dgemm_nt_inc.yaml_file_name.format(str(file_idx))
                        if K == '256' or K == '384':
                            dict[K]['content'] = dgemm_nt_inc.yaml_prefix_str.format('True')
                        else:
                            dict[K]['content'] = dgemm_nt_inc.yaml_prefix_str.format('False')
                        file_idx += 1
                        
                        if K == '128' and rltu_content != '':
                            dict[K]['content'] += rltu_content
                    for LDA in dict_parsed_info[M][N][K]:
                        for LDB in dict_parsed_info[M][N][K][LDA]:
                            for LDC in dict_parsed_info[M][N][K][LDA][LDB]:
                                for LDD in dict_parsed_info[M][N][K][LDA][LDB][LDC]:
                                    dict[K]['content'] += '          - Exact: '
                                    dict[K]['content'] += dict_parsed_info[M][N][K][LDA][LDB][LDC][LDD]['CONTENT']
    
    if rltu_content != '' and not '128' in dict:
        dict['128'] = {}
        dict['128']['file_name'] = dgemm_nt_inc.yaml_file_name.format(str(file_idx))
        file_idx += 1
        dict['128']['content'] = dgemm_nt_inc.yaml_prefix_str.format('False')
        dict['128']['content'] += rltu_content
        
    for K in dict:
        dict[K]['content'] += dgemm_nt_inc.yaml_postfix_str
        out_path = gflags.FLAGS.output_folder + "/" + dict[K]['file_name']
        saveYamlFile(dict[K]['content'], out_path)
            

# input: 
# NN, M, N, K, LDA, LDB, LDC, LDD
# LLNU, M, N, LDA, LDB
def generateNN(nn_parse_info):
    file_idx = gflags.FLAGS.dgemm_nn_inc_start_idx
    file_name = dgemm_nn_inc.yaml_file_name.format(str(file_idx))
    
    if 'NN' in nn_parse_info:
        content = dgemm_nn_inc.yaml_prefix_str
        dict_parsed_info = nn_parse_info['NN']
        for M in dict_parsed_info:
            for N in dict_parsed_info[M]:
                for K in dict_parsed_info[M][N]:
                    for LDA in dict_parsed_info[M][N][K]:
                        for LDB in dict_parsed_info[M][N][K][LDA]:
                            for LDC in dict_parsed_info[M][N][K][LDA][LDB]:
                                for LDD in dict_parsed_info[M][N][K][LDA][LDB][LDC]:
                                    content += '          - Exact: '
                                    content += dict_parsed_info[M][N][K][LDA][LDB][LDC][LDD]['CONTENT']
        content += dgemm_nn_inc.yaml_postfix_str
        out_path = gflags.FLAGS.output_folder + "/" + file_name
        saveYamlFile(content, out_path)
                                    
    
    
def generateYamlFile(dict_parsed_info):
    format_list = dict_parsed_info.keys()
    if len(format_list) == 0:
        print("no data!")
        return
            
    generateNT(dict_parsed_info)
    generateNN(dict_parsed_info)

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
def main():
    print("Start generate yaml file...")
    
    file_postfix_str = os.path.splitext(gflags.FLAGS.input_file)[-1][1:]
    parsed_info = {}
    if file_postfix_str == 'xlsx' or file_postfix_str == 'xls':
        #parse xlsx file
        parsed_info = parse_xlsx.parse(gflags.FLAGS.input_file, gflags.FLAGS.sheet_name)
    elif file_postfix_str == 'txt':
        #todo: parse txt file
        pass
    
    generateYamlFile(parsed_info)

    print("Generate yaml file completed!")


if __name__ == '__main__':

    try:
        argv = gflags.FLAGS(sys.argv)
    except gflags.FlagsError as e:
        print(gflags.FLAGS)
        sys.exit(1)
    main()