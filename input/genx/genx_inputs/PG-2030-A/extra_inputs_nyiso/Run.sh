#!/bin/bash -l
#SBATCH --job-name=p4LowRE_MGA                    # create a short name for your job
#SBATCH --nodes=1                           # node count
#SBATCH --ntasks=1                          # total number of tasks across all nodes
#SBATCH --cpus-per-task=1                   # cpu-cores per task (>1 if multi-threaded tasks)
#SBATCH --mem-per-cpu=30G                    # memory per cpu-core
#SBATCH --time=2-01:00:00                     # total run time limit (HH:MM:SS)
#SBATCH --output=output-file-%j-%x.log
#SBATCH --error=error-file-%j-%x.log

module add julia/1.8.5
module add gurobi/9.5.2
module add gnu12/12.2.0

julia --project=. /data/home/secheva1/p1MGA/GenX-main1/Example_Systems/SPIEDIE/NY_Powergenome_RE_Low_Cost/Run.jl


date
