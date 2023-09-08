import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import multiprocessing

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

def convertPxToCm(df: pd.DataFrame, column: str, pixelsInUnit, cmApart):
    df[column + "Cm"] = df[column] / pixelsInUnit * cmApart

def createSecondsColumn(df: pd.DataFrame, fps: float):
    df['seconds'] = df['frame'] / fps

def smoothHighestXPos(df: pd.DataFrame, column: str, windowSize: int):
    df[column + "Smooth"] = df[column].rolling(window=windowSize).mean()

def plotXPos(ax, df: pd.DataFrame, title: str):
    # Line plot for x pos
    ax.plot(df['seconds'], df['highestXPosSmoothCm'])
    out = ax.set(title=title)

    print("plotXPos done")
    return out

def createAndSavePlots(args):
    df, title, exportDir = args

    fig, ax = plt.subplots()
    plotXPos(ax, df, title)
    fig.savefig(f'{exportDir}/highestXPos.png')

    print("createAndSavePlots done")
    return

def postProcess(highestXPosList: list, pixelsInUnit, cmApart, fps, title: str, exportDir: str):
    # Auto crop
    print("auto crop")
    highestXPosList = autoCrop(highestXPosList)

    # Create dataframe
    print("create dataframe")
    df = highestXPosListToPd(highestXPosList)

    # Create seconds column
    print("create seconds column")
    createSecondsColumn(df, fps)

    # Smoothen highestXPos
    print("smoothen highestXPos")
    smoothHighestXPos(df, "highestXPos", 100)

    # Convert pixels to cm
    print("convert pixels to cm", pixelsInUnit, cmApart)
    convertPxToCm(df, "highestXPosSmooth", pixelsInUnit, cmApart)

    # Export CSV and plots to exportDir
    print("exporting")

    df.to_csv(f'{exportDir}/highestXPos.csv', mode="w")

    # Matplotlib savefig doesn't work in a thread
    # https://britishgeologicalsurvey.github.io/science/python-forking-vs-spawn/
    with multiprocessing.get_context("spawn").Pool() as pool:
        pool.map(createAndSavePlots, [(df, title, exportDir)])