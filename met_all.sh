for file in data/MC_ZNuNu/*
do
  python3 src/main.py met -fp "$file" -tp data/triggerlists/MET_triggers.txt -o out_met -pb
done