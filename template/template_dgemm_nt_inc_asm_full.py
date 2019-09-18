# template for dgemm_nt_inc_asm_full
yaml_prefix_str = '''GlobalParameters:
  MinimumRequiredVersion: 4.9.0
  PrintLevel: 1
  ForceRedoBenchmarkProblems: True
  ForceRedoLibraryLogic: True
  ForceRedoLibraryClient: True
  CMakeBuildType: Release
  EnqueuesPerSync: 1
  SyncsPerBenchmark: 2
  LibraryPrintDebug: False
  NumElementsToValidate: 0
  ValidationMaxToPrint: 4
  ValidationPrintValids: False
  ShortNames: False
  MergeFiles: True
  Platform: 0
  Device: 0
  KernelTime: True
  PinClocks: False
  SleepPercent: 0
  DataInitTypeBeta : 2
  CEqualD: True
# PrintSolutionRejectionReason: True
# SolutionSelectionAlg: 1
# PrintWinnersOnly: 1
# ExitOnFails: 0

BenchmarkProblems:

  ########################################
  # NT
  ########################################
  -
    - # ProblemType
      OperationType: GEMM
      DataType: d
      TransposeA: False
      TransposeB: True
      UseBeta: True
      Batched: True

    - # BenchmarkProblemSizeGroup - Feb 24 version1 & version2
      InitialSolutionParameters:
      BenchmarkCommonParameters:
        - BufferLoad: [True]
        - BufferStore: [True]
        - KernelLanguage: ["Assembly"]
        - EdgeType: ["ShiftPtr"]
        - LoopTail: [True]
        - ReplacementKernel: [{}]
      ForkParameters:
        - FractionalLoad: [True]
        - PrefetchGlobalRead: [True]
        - PrefetchLocalRead: [True, False]
        - PersistentKernel: [0]
        - SuppressNoLoadLoop: [True, False] 
        - StaggerU: [0]
        - ThreadTile:
          - [ 4, 4 ]
          - [ 6, 4 ]
          - [ 4, 6 ]
          - [ 6, 6 ]
          - [ 8, 4 ]
          - [ 4, 8 ]
        - WorkGroup:
          - [ 32, 16,  1 ]
          - [ 16,  8,  1 ]
          - [  8, 16,  1 ]
          - [ 16, 16,  1 ]
          - [ 16, 32,  1 ]
        - WorkGroupMapping: [1, 4, 8]
        - DepthU: [ 4, 8 ]
        - VectorWidth: [-1]
      BenchmarkForkParameters:
      JoinParameters:
      BenchmarkJoinParameters:
      BenchmarkFinalParameters:
        - ProblemSizes:\n'''

yaml_postfix_str = '''LibraryLogic:
    ScheduleName: "vega20"
    DeviceNames: ["Device 66a0", "Device 66a1", "Device 66a7", "Vega 20"]
    ArchitectureName: "gfx906"

#   ScheduleName: "vega10"
#   DeviceNames: ["Device 6863", "Device 6862", "Device 687f", "Device 6860", "Device 6861", "Vega 10 XTX [Radeon Vega Frontier Edition]", "Vega [Radeon RX Vega]"]
#   ArchitectureName: "gfx900"

#   ScheduleName: "mi25"
#   DeviceNames: ["Device 6860"]
#   ArchitectureName: "gfx900"

#   ScheduleName: "r9nano"
#   DeviceNames: ["Device 7300"]
#   ArchitectureName: "gfx803"

#   ScheduleName: "hip"
#   DeviceNames: ["Device 0000"]
#   ArchitectureName: "fallback"

LibraryClient:\n'''

yaml_file_name = "rocblas_dgemm_nt_inc{}_asm_full.yaml"