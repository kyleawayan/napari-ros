#!/bin/bash
# Temporary test scipt to compare analysis results

# specify the file paths
truth="/Users/kyle/Documents/ros_benchmark/data/DSC_0201_Test_No_250/highestXPos.csv"
toTest="/Users/kyle/Documents/ros_benchmark/data/TEST250ANALYSISBRANCHTEST/highestXPos.csv"

# run the diff command
diff --color=auto $truth $toTest