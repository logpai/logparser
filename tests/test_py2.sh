#!/bin/bash

printf "========== Testing =========="
cd ../demo

printf "\n========== AEL ==========\n"
python AEL_demo.py

printf "\n========== Drain ==========\n"
python Drain_demo.py

printf "\n========== IPLoM ==========\n"
python IPLoM_demo.py

printf "\n========== LenMa ==========\n"
python LenMa_demo.py

printf "\n========== LFA ==========\n"
python LFA_demo.py

printf "\n========== LKE ==========\n"
python LKE_demo.py

printf "\n========== LogCluster ==========\n"
python LogCluster_demo.py

printf "\n========== LogMine ==========\n"
python LogMine_demo.py

printf "\n========== LogSig ==========\n"
python LogSig_demo.py

printf "\n========== SHISO ==========\n"
python SHISO_demo.py

printf "\n========== SLCT ==========\n"
python SLCT_demo.py

printf "\n========== Spell ==========\n"
python Spell_demo.py

printf "\n========== Testing done =========\n"