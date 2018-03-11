import os
import sys
import pip
import argparse
import subprocess

REPOS = [
		"https://bitbucket.org/fenics-project/fiat.git",
		"https://bitbucket.org/fenics-project/ufl.git",
		"https://bitbucket.org/fenics-project/dijitso.git",
		"https://bitbucket.org/fenics-project/ffc.git",
		"https://github.com/blechta/tsfc.git",
		"https://github.com/blechta/COFFEE.git",
		"https://github.com/blechta/FInAT.git",
		"https://bitbucket.org/fenics-project/dolfin.git",
		"https://github.com/pybind/pybind11.git"
	]

PIP_INSTALLS = [
	"fiat",
	"ufl",
	"dijitso",
	"ffc",
	"tsfc",
	"COFFEE",
	"FInAT"
]

def print_stdout(args, raise_on_nonzero=False, **kwargs):
	sys.stdout.flush()
	kwargs["stdout"] = subprocess.PIPE
	process = subprocess.Popen(args, **kwargs)
	while True:
		output = process.stdout.readline()
		if len(output.strip()) == 0 and process.poll() is not None:
			break
		if output:
			print(output.strip().decode())

	rc = process.poll()
	sys.stdout.flush()

	if raise_on_nonzero and rc != 0:
		raise RuntimeError(f"Subprocess {args[0]} did not terminate successfully.")

	return process.poll()

def clone_repos(src_directory: str):
	for repo in REPOS:
		print_stdout(["git", "clone", repo], cwd=src_directory)
		print("")

	return 0

def pip_install(src_dir: str):
	for pkg in PIP_INSTALLS:
		pkg_path = os.path.join(src_dir, pkg)
		pip.main(["install", "-e", f"{pkg_path}"])
		print("")

	for pkg in ["six", "singledispatch", "pulp"]:
		pip.main(["install", pkg])
		print("")

	return 0

def pybind_build(src_dir: str, build_dir: str, pybind_dir: str):
	pybind_build_path = os.path.join(build_dir, "pybind11")
	os.makedirs(pybind_build_path, exist_ok=True)

	print_stdout(["cmake", "-DPYBIND11_TEST=off", 
		f"-DCMAKE_INSTALL_PREFIX={pybind_dir}",
		f"{src_dir}/pybind11"],
		cwd=pybind_build_path)
	print("")

	make_return = print_stdout(["make", "install"], cwd=pybind_build_path)
	print("")

	if make_return != 0:
		print("pybind make install did not return successfully!")
		return 1

	return 0

def dolfin_build(src_dir: str, build_dir: str, dolfin_dir: str):
	dolfin_build_path = os.path.join(build_dir, "dolfin")
	os.makedirs(dolfin_build_path, exist_ok=True)
	
	try:
		print_stdout(["cmake",
			f"-DCMAKE_INSTALL_PREFIX={dolfin_dir}",
			f"{src_dir}/dolfin"],
			raise_on_nonzero=True,
			cwd=dolfin_build_path
		)

		print_stdout(["make", "j4"], raise_on_nonzero=True, cwd=dolfin_build_path)
		print_stdout(["make", "install"], raise_on_nonzero=True, cwd=dolfin_build_path)
	except RuntimeError as err:
		print(err)
		return 1

	"""
	cd "${SRC_DIR}/dolfin/python"
	export PYBIND11_DIR="${PYBIND_DIR}"
	export DOLFIN_DIR="${DOLFIN_DIR}"
	pip3 install -e .

	return 0
	"""

	return 0

def main():
	parser = argparse.ArgumentParser(description="install and set up an environment for FEniCS from git")
	parser.add_argument("-r", "--repo-dir", type=str, help="Directory where source directories (repositories) will be stored.")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-l", "--local", action="store_true", help="Don't clone any repositories, use local files.")
	group.add_argument("-co", "--clone-only", action="store_true", help="Only clone the required repositories, no install/build.")
	parser.add_argument("install_prefix", type=str, help="FEniCS will be installed into this folder. If not specified, the current folder will be used.", nargs='?')
	group2 = parser.add_mutually_exclusive_group()
	group2.add_argument("--internal-stage-one", action="store_true")
	group2.add_argument("--internal-stage-two", action="store_true")

	args = parser.parse_args()

	FENICS_DIR = args.install_prefix
	SRC_DIR = args.repo_dir
	BUILD_DIR = None

	if FENICS_DIR is None:
		FENICS_DIR = os.getcwd()

	if SRC_DIR is None:
		SRC_DIR = os.path.join(FENICS_DIR, "src")

	print(args)
	print("")

	VENV_DIR = os.path.join(FENICS_DIR, "fenics_env")
	BUILD_DIR = os.path.join(FENICS_DIR, "build")
	PYBIND_DIR = os.path.join(FENICS_DIR, "include", "pybind11")
	DOLFIN_DIR = os.path.join(FENICS_DIR, "dolfin")

	print(sys.argv)
	print("")

	if args.clone_only is True:
		print("Only cloning repositories...")
		print()

		os.makedirs(SRC_DIR, exist_ok=True)
		clone_repos(SRC_DIR)
		return

	if args.internal_stage_one is False and args.internal_stage_two is False:
		os.makedirs(FENICS_DIR, exist_ok=True)
		os.makedirs(SRC_DIR, exist_ok=True)

		clone_repos(SRC_DIR)

		# Create a virtual environment
		import virtualenv
		virtualenv.create_environment(VENV_DIR)
		print("Switching to virtual environment...")

		print("Stage 1")
		print_stdout([os.path.join(VENV_DIR, "bin", "python3"), os.path.basename(sys.argv[0]), "--internal-stage-one", *sys.argv[1:]], cwd=os.getcwd())

		print("Stage 2")
		print_stdout([os.path.join(VENV_DIR, "bin", "python3"), os.path.basename(sys.argv[0]), "--internal-stage-two", *sys.argv[1:]], cwd=os.getcwd())
		return

	elif args.internal_stage_one is True:
		pip_install(SRC_DIR)
		return

	elif args.internal_stage_two is True:
		pybind_build(SRC_DIR, BUILD_DIR, PYBIND_DIR)
		print("")
		dolfin_build(SRC_DIR, BUILD_DIR, DOLFIN_DIR)

		print("")
		print("Installed packages in virtual environment:")
		pip.main(["list", "--format=columns"])

		print("")
		print(f"Activate FEniCS python virtualenv using 'source {FENICS_DIR}/fenics_env/bin/activate'")
		print(f"Activate DOLFIN build environment using 'source {FENICS_DIR}/dolfin/share/dolfin/dolfin.conf'")
		return
	
if __name__ == '__main__':
	main()