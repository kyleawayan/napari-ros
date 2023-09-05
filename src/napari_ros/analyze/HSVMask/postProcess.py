import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

def highestXPosListToPd(highestXPosList: list):
    df = pd.DataFrame(columns=['frame', 'highestXPos'])

    # Fill frame column with numbers 1 to len(highestXPosList)
    df['frame'] = range(1, len(highestXPosList) + 1)

    # Fill highestXPos column with highestXPosList
    df['highestXPos'] = highestXPosList

    return df

def autoCrop(highestXPosList: list) -> list:
    # Using numpy temporarily for array operations
    data = np.array(highestXPosList)

    # Get the max index
    maxIndex = data.argmax()

    # Get the first index where there is a value above zero
    firstIndex = np.where(data > 0)[0][0]

    # TODO: Make sure to check weird edge cases
    dataTrim = data[firstIndex:maxIndex]
    
    return dataTrim.tolist()

def convertPxToCm(df: pd.DataFrame, pixelsInUnit, cmApart):
    df['highestXPos'] = df['highestXPos'] / pixelsInUnit * cmApart
    return df

def createSecondsColumn(df: pd.DataFrame, fps: float):
    df['seconds'] = df['frame'] / fps
    return df

def createHighestXPosPlot(df: pd.DataFrame, title: str):
    # Line plot
    fig, ax = plt.subplots()
    ax.plot(df['seconds'], df['highestXPos'])
    ax.set(xlabel='seconds', ylabel='highestXPos', title=title)
    ax.grid()

    return fig

def postProcess(highestXPosList: list, pixelsInUnit, cmApart, fps, title: str, exportDir: str):
    # Auto crop
    print("auto crop")
    highestXPosList = autoCrop(highestXPosList)

    # Create dataframe
    print("create dataframe")
    df = highestXPosListToPd(highestXPosList)

    # Create seconds column
    print("create seconds column")
    df = createSecondsColumn(df, fps)

    # Convert pixels to cm
    print("convert pixels to cm")
    df = convertPxToCm(df, pixelsInUnit, cmApart)

    # Create plots
    print("create plots")
    highestXPosPlot = createHighestXPosPlot(df, title)

    # Export CSV and plots to exportDir
    print("exporting")

    df.to_csv(f'{exportDir}/highestXPos.csv', mode="w")
    highestXPosPlot.savefig(f'{exportDir}/highestXPos.png')