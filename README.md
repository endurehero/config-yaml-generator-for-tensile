# config-yaml-generator-for-tensile
a utility to generate yaml files based on the trsm/dgemm sizes in excel documents. At present, in addition to LLNU format is still under development, other formats NN/NT/RLTU have been fully supported.  

Usage:  
1.	Install the dependences. Dependences library include: xlrd and gflags. If your environment lacks dependent libraries, you can install them using scripts in the root directory:  
$ cd ./yaml_generator  
$ chmod +x ./install_depend.sh  
$ sudo ./install_depend.sh  
  
2.	Run yaml_generator.py to generate yaml file.  
You can use arg --help to get help info like below:  
$ python ./yaml_generator.py --help  
  
This is the command which i used to process 0422 sheet.  
$ python ./yaml_generator.py --input_file=../rocblas-matrix-size-request-and-schedule-0422.xlsx --dgemm_nt_inc_start_idx=2 --sheet_name=201900422 --output_folder=./output  

Finally, 4 yaml files  will be generated in the ‘output’ folder.  
