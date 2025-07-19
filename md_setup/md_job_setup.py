# md_job_setup.py
import os
import shutil
from textwrap import dedent

from ase import io  # For .cif -> .data conversion

class MDJobSetup:
    """
    Sets up LAMMPS MD jobs from a subset of .cif or .data files in a folder.

    If a file is .cif:
      - We convert it in-memory directly to .data in the job folder 
        (i.e., never write .data back to the original folder).
    If a file is already .data:
      - We copy it into the job folder.

    This way, the .data only ever appears in the final job folder.
    """

    def __init__(
        self,
        main_dir="2024-12-06_production_mace_small",
        in_lammps_template_path=None,
        submit_script_template_path=None
    ):
        """
        :param main_dir: Base folder where per-job directories will be placed.
        :param in_lammps_template_path: Path to a file containing 'in.lammps' template, or None for default.
        :param submit_script_template_path: Path to a file containing 'submit.sh' template, or None for default.
        """
        self.main_dir = main_dir
        os.makedirs(self.main_dir, exist_ok=True)

        # --- Load or set default in.lammps template ---
        if in_lammps_template_path:
            with open(in_lammps_template_path, 'r') as f:
                self.in_lammps_template = f.read()
        else:
            default_in_path = "/Users/erik/Desktop/10_semester/master_thesis/templates/md/in.lammps.template"
            with open(default_in_path, 'r') as f:
                self.in_lammps_template = f.read()

        # --- Load or set default submit.sh template ---
        if submit_script_template_path:
            with open(submit_script_template_path, 'r') as f:
                self.submit_script_template = f.read()
        else:
            default_submit_path = "/Users/erik/Desktop/10_semester/master_thesis/templates/md/submit.sh.template"
            with open(default_submit_path, 'r') as f:
                self.submit_script_template = f.read()

    def _convert_cif_in_memory(self, cif_path, data_path):
        """
        Convert the .cif at 'cif_path' to a LAMMPS .data file at 'data_path', using ASE in memory.
        """
        atoms = io.read(cif_path)
        atoms.set_pbc([True, True, True])
        io.write(data_path, atoms, format='lammps-data')
        print(f"Converted {cif_path} => {data_path}")

    def create_jobs(
        self,
        data_folder,
        temperature_initial=300,
        temperature_target=1500,
        equilibration_steps=25000,
        configurations=None,
        selected_files=None
    ):
        """
        Creates LAMMPS job directories for a chosen subset of .cif/.data files in 'data_folder'.

        If selected_files is None, we use all .cif/.data in 'data_folder'.
        For each file:
          1) Create a subfolder named like "basename_T<temp>" (or you can remove the temp part).
          2) If .cif => convert directly to .data in that subfolder. 
             If .data => copy it to that subfolder.
          3) Write in.lammps from template, substituting {temp_init}, {temp}, etc.
          4) Write submit.sh from template, substituting HPC config, etc.
          5) Append lines to 'launch_all_jobs.sh'.

        :param data_folder: Directory containing .cif or .data files.
        :param temperature_initial: e.g. 300 K (initial velocity).
        :param temperature_target: e.g. 1800 K or 2400 K.
        :param equilibration_steps: Number of steps in equilibration run
        :param configurations: HPC config list. e.g. [{'nodes':1, 'tasks':1, 'cpus_per_task':8}]
        :param selected_files: A list of specific filenames or None => process all .cif/.data.
        """
        if configurations is None:
            configurations = [{'nodes': 1, 'tasks': 1, 'cpus_per_task': 8}]

        # 1) Determine which files we will handle
        if selected_files is not None:
            # Validate they exist
            for name in selected_files:
                if not os.path.isfile(os.path.join(data_folder, name)):
                    raise FileNotFoundError(f"{name} not found in {data_folder}")
            files_to_process = selected_files
        else:
            # All .cif or .data
            all_files = os.listdir(data_folder)
            files_to_process = [
                f for f in all_files
                if f.endswith(".cif") or f.endswith(".data")
            ]

        print("Files selected for job creation:", files_to_process)

        # 2) Create or append to master launcher script
        launcher_script_path = os.path.join(self.main_dir, "launch_all_jobs.sh")
        mode = 'a' if os.path.exists(launcher_script_path) else 'w'
        with open(launcher_script_path, mode) as launcher:
            if mode == 'w':
                launcher.write("#!/bin/bash\n\n")

            # 3) HPC config loop
            for cfg in configurations:
                # 4) For each file
                for fname in files_to_process:
                    base, ext = os.path.splitext(fname)
                    # job folder name includes temperature (optional)
                    job_folder_name = f"{base}_T{int(temperature_target)}"
                    job_folder = os.path.join(self.main_dir, job_folder_name)
                    os.makedirs(job_folder, exist_ok=True)

                    # 5) Decide how to get the .data
                    # If it's .cif => convert in the job folder
                    if ext == ".cif":
                        source_cif = os.path.join(data_folder, fname)
                        data_filename = base + ".data"
                        data_dest = os.path.join(job_folder, data_filename)
                        self._convert_cif_in_memory(source_cif, data_dest)
                    else:
                        # It's .data => just copy it
                        source_data = os.path.join(data_folder, fname)
                        data_filename = fname  # keep same name
                        data_dest = os.path.join(job_folder, data_filename)
                        shutil.copy(source_data, data_dest)

                    # 6) Write in.lammps using the data_filename
                    in_content = self.in_lammps_template.format(
                        temp_init=temperature_initial,
                        temp=temperature_target,
                        steps=equilibration_steps,
                        data_file=data_filename,
                        data_name=base
                    )
                    in_path = os.path.join(job_folder, "in.lammps")
                    with open(in_path, 'w') as f_in:
                        f_in.write(in_content)

                    # 7) Write submit.sh
                    submit_content = self.submit_script_template.format(
                        data_name=base,
                        nodes=cfg['nodes'],
                        tasks=cfg['tasks'],
                        cpus_per_task=cfg['cpus_per_task']
                    )
                    submit_path = os.path.join(job_folder, "submit.sh")
                    with open(submit_path, 'w') as f_submit:
                        f_submit.write(submit_content)
                    os.chmod(submit_path, 0o755)

                    # 8) Add lines to the master launcher script
                    launcher.write(f"cd {job_folder_name}\n")
                    launcher.write("sbatch submit.sh\n")
                    launcher.write("cd ..\n\n")

        os.chmod(launcher_script_path, 0o755)
        print(f"All job folders created in '{self.main_dir}'.")
        print(f"Use 'bash launch_all_jobs.sh' from within '{self.main_dir}' to submit the jobs.")
