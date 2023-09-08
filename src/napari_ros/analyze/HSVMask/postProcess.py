import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt
import multiprocessing
import json

# Allow for JSON encoding of non-JSON serializable objects like numpy
class JSONEncoderCustom(json.JSONEncoder):
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

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

def measureSpeed(df: pd.DataFrame, column: str):
    """
    Seconds column must be created first
    """
    df[column + "Speed"] = df[column].diff() / df['seconds'].diff()

def plotXPos(ax, df: pd.DataFrame, title: str):
    # Line plot for x pos
    out = ax.plot(df['seconds'], df['highestXPosSmoothCm'])
    out = ax.set(title=title)
    # x label is in plotXSpeed
    out = ax.set(ylabel="leading edge pos. (cm)")

    print("plotXPos done")
    return out

def plotXSpeed(ax, df: pd.DataFrame, title: str):
    # Line plot for x speed
    out = ax.plot(df['seconds'], df['highestXPosSmoothCmSpeed'])
    out = ax.set(title=title)
    out = ax.set(xlabel="time (seconds)", ylabel="leading edge speed (cm/s)")

    print("plotXSpeed done")
    return out

def createAndSavePlots(args):
    df, title, exportDir = args

    fig, axs = plt.subplots(2, 1, figsize=(10, 10))
    plotXPos(axs[0], df, title + " Flame Leading Edge Position")
    plotXSpeed(axs[1], df, title + " Flame Leading Edge Speed")
    fig.savefig(f'{exportDir}/highestXPos.png')

    print("createAndSavePlots done")
    return

def gatherStatistics(df: pd.DataFrame):
    """
    Returns a dictionary of statistics
    """
    stats = {}

    stats["mean"] = df['highestXPosSmoothCmSpeed'].mean()
    stats["median"] = df['highestXPosSmoothCmSpeed'].median()
    stats["std"] = df['highestXPosSmoothCmSpeed'].std()
    stats["min"] = df['highestXPosSmoothCmSpeed'].min()
    stats["max"] = df['highestXPosSmoothCmSpeed'].max()

    return stats

def postProcess(highestXPosList: list, config, title: str, exportDir: str):
    pixelsInUnit = config["pixelsInUnit"]
    cmApart = config["cmApart"]
    fps = config["fps"]

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

    # Measure speed
    print("measure speed")
    measureSpeed(df, "highestXPosSmoothCm")

    # Export CSV
    print("exporting csv")
    df.to_csv(f'{exportDir}/highestXPos.csv', mode="w")

    # Metadata
    metadata = {}
    metadata["config"] = config
    metadata["highestXPosSmoothCmSpeedStats"] = gatherStatistics(df)
    metadata["title"] = title
    metadata["exportDir"] = exportDir
    # TODO: Store latest commit ID

    # Export metadata into JSON
    print("exporting metadata")
    with open(f'{exportDir}/metadata.json', 'w') as f:
        json.dump(metadata, f, cls=JSONEncoderCustom, indent=4)

    # Matplotlib savefig doesn't work in a thread
    # https://britishgeologicalsurvey.github.io/science/python-forking-vs-spawn/
    with multiprocessing.get_context("spawn").Pool() as pool:
        pool.map(createAndSavePlots, [(df, title, exportDir)])