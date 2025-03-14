#!/usr/bin/env python3
# 只想arg_list中的pass，每次都从input.ll开始执行，而不是上一个pass
import subprocess
import os
import argparse
import tempfile
import shutil

file_index = 0;

# 检查工具是否可用
def check_tool_available(tool_name):
    try:
        subprocess.run([tool_name, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError:
        raise RuntimeError(f"{tool_name} not found. Please ensure LLVM is installed and {tool_name} is in your PATH.")

# 运行 opt 并返回输出文件路径
def run_opt_pass(input_file, pass_name):
    global file_index
    output_file = f"output_{file_index:03d}_{pass_name}.ll"
    file_index = file_index + 1

    # 构建并运行 opt 命令
    cmd = ["opt", "-S", f"-{pass_name}", input_file, "-o", output_file]
    print(f"Running opt command: {' '.join(cmd)}")
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        print(f"Error running pass {pass_name}: {result.stderr}")
        os.remove(output_file)
        return None

    return output_file

# 使用 llvm-diff 比较两个 IR 文件
def compare_ir_with_llvm_diff(file1, file2):
    cmd = ["llvm-diff", file1, file2]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # llvm-diff 返回 0 表示文件相同，非 0 表示有差异
    return result.returncode == 0

# 主函数：分析哪些 Pass 起作用
# order 表面是依次执行，还是每次的输入都是Input.ll
def analyze_passes(input_file, pass_list, order):
    effective_passes = []
    ineffective_passes = []

    # 逐个运行 Pass 并检查效果
    for pass_name in pass_list:
        print(f"\nAnalyzing pass: {pass_name}")
        output_file = run_opt_pass(input_file, pass_name)

        if output_file is None:
            print(f"Skipping {pass_name} due to execution error.")
            ineffective_passes.append(pass_name)
            continue

        # 使用 llvm-diff 比较
        is_identical = compare_ir_with_llvm_diff(input_file, output_file)

        if is_identical:
            ineffective_passes.append(pass_name)
            print(f"Pass {pass_name} had no effect (IR unchanged).")
        else:
            effective_passes.append(pass_name)
            print(f"Pass {pass_name} modified the IR.")

        # 删除临时文件
        # os.remove(output_file)
        if (order):
            input_file = output_file

    return effective_passes, ineffective_passes

# 打印结果
def print_results(effective_passes, ineffective_passes):
    print("\n=== Results ===")
    print("Passes that had an effect:")
    for p in effective_passes:
        print(f"  - {p}")
    print("Passes that had no effect:")
    for p in ineffective_passes:
        print(f"  - {p}")

# 命令行参数解析
def main():
    parser = argparse.ArgumentParser(description="Analyze which LLVM passes affect a given .ll file using llvm-diff.")
    parser.add_argument("input_file", nargs = '?', help="Path to the input .ll file", default = "input.ll")
    parser.add_argument("--order", action="store_true", help="Order execute the arg passes, default is false")
    args = parser.parse_args()

    input_file = args.input_file
    order = args.order

#    pass_list = ["bdce", "dce", "inline", "simplifycfg"]
#   opt O1  # opt -S input.ll -o output.ll -O1 -debug-pass=Structure 的输出
    pass_list = [
    "tti", "targetlibinfo", "tbaa", "scoped-noalias", "assumption-cache-tracker",
    "profile-summary-info", "forceattrs", "inferattrs", "ipsccp", "called-value-propagation",
    "attributor", "globalopt", "domtree", "mem2reg", "deadargelim", "basicaa", "aa", "loops",
    "lazy-branch-prob", "lazy-block-freq", "opt-remark-emitter", "instcombine", "simplifycfg",
    "basiccg", "globals-aa", "prune-eh", "always-inline", "functionattrs", "domtree", "sroa",
    "basicaa", "aa", "memoryssa", "early-cse-memssa", "basicaa", "aa", "lazy-value-info",
    "jump-threading", "correlated-propagation", "simplifycfg", "domtree", "basicaa", "aa",
    "loops", "lazy-branch-prob", "lazy-block-freq", "opt-remark-emitter", "instcombine",
    "libcalls-shrinkwrap", "loops", "branch-prob", "block-freq", "lazy-branch-prob",
    "lazy-block-freq", "opt-remark-emitter", "pgo-memop-opt", "basicaa", "aa", "loops",
    "lazy-branch-prob", "lazy-block-freq", "opt-remark-emitter", "tailcallelim", "simplifycfg",
    "reassociate", "domtree", "loops", "loop-simplify", "lcssa-verification", "lcssa", "basicaa",
    "aa", "scalar-evolution", "loop-rotate", "licm", "loop-unswitch", "simplifycfg", "domtree",
    "basicaa", "aa", "loops", "lazy-branch-prob", "lazy-block-freq", "opt-remark-emitter",
    "instcombine", "loop-simplify", "lcssa-verification", "lcssa", "scalar-evolution", "indvars",
    "loop-idiom", "loop-deletion", "loop-unroll", "phi-values", "memdep", "memcpyopt", "sccp",
    "demanded-bits", "bdce", "basicaa", "aa", "lazy-branch-prob", "lazy-block-freq",
    "opt-remark-emitter", "instcombine", "lazy-value-info", "jump-threading", "correlated-propagation",
    "basicaa", "aa", "phi-values", "memdep", "dse", "loops", "loop-simplify", "lcssa-verification",
    "lcssa", "basicaa", "aa", "scalar-evolution", "licm", "postdomtree", "adce", "simplifycfg",
    "domtree", "basicaa", "aa", "loops", "lazy-branch-prob", "lazy-block-freq", "opt-remark-emitter",
    "instcombine", "barrier", "basiccg", "rpo-functionattrs", "globalopt", "globaldce", "basiccg",
    "globals-aa", "float2int", "domtree", "loops", "loop-simplify", "lcssa-verification", "lcssa",
    "basicaa", "aa", "scalar-evolution", "loop-rotate", "loop-accesses", "lazy-branch-prob",
    "lazy-block-freq", "opt-remark-emitter", "loop-distribute", "branch-prob", "block-freq",
    "scalar-evolution", "basicaa", "aa", "loop-accesses", "demanded-bits", "lazy-branch-prob",
    "lazy-block-freq", "opt-remark-emitter", "loop-vectorize", "loop-simplify", "scalar-evolution",
    "aa", "loop-accesses", "lazy-branch-prob", "lazy-block-freq", "loop-load-elim", "basicaa", "aa",
    "lazy-branch-prob", "lazy-block-freq", "opt-remark-emitter", "instcombine", "simplifycfg", "domtree",
    "basicaa", "aa", "loops", "lazy-branch-prob", "lazy-block-freq", "opt-remark-emitter", "instcombine",
    "loop-simplify", "lcssa-verification", "lcssa", "scalar-evolution", "loop-unroll", "lazy-branch-prob",
    "lazy-block-freq", "opt-remark-emitter", "transform-warning", "alignment-from-assumptions",
    "strip-dead-prototypes", "domtree", "loops", "branch-prob", "block-freq", "loop-simplify",
    "lcssa-verification", "lcssa", "basicaa", "aa", "scalar-evolution", "block-freq", "loop-sink",
    "lazy-branch-prob", "lazy-block-freq", "opt-remark-emitter"
    ]
    print(f"pass_list: {pass_list}")

    # 验证输入文件是否存在
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist.")
        return

    # 检查 opt 和 llvm-diff 工具
    check_tool_available("opt")
    check_tool_available("llvm-diff")

    # 分析 Pass
    effective_passes, ineffective_passes = analyze_passes(input_file, pass_list, order)

    # 输出结果
    print_results(effective_passes, ineffective_passes)

def movefile():
    # 获取当前工作目录
    current_directory = os.getcwd()

    # 创建 output 文件夹（如果它不存在）
    output_dir = os.path.join(current_directory, 'output')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 遍历当前目录中的所有文件
    for filename in os.listdir(current_directory):
        if filename.startswith('output_'):
            # 构建源文件和目标文件的路径
            source_file = os.path.join(current_directory, filename)
            destination_file = os.path.join(output_dir, filename)

            # 移动文件到 output 文件夹
            shutil.move(source_file, destination_file)



if __name__ == "__main__":
    main()
    movefile()
