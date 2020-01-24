#!/usr/bin/python3.5

import os, pickle, sqlite3
import matplotlib.pyplot as plt
import tkinter as tk
from argparse import ArgumentParser
from multiprocessing import Process


def power_plot(name, values, timestamps, width, height, corrects, incorrects, directory, table=None):    
    plt.figure(figsize=(width,height))
    plt.suptitle(name)
    plt.plot(timestamps, values, color='black')
    plt.xlabel('Time')
    plt.ylabel('Power?')
    if table is not None:
        for a in corrects:
            plt.axvline(x=a, color='purple')
        for b in incorrects:
            plt.axvline(x=b, color='orange')
    
    plt.savefig(name)
    plt.close()


def ratio_plot(name, ratios, ceiling, timestamps, width, height, corrects, incorrects, directory, table=None):
    remove_these = []
    new_timestamps = timestamps.copy()
    for x in range(len(ratios)):
        if abs(ratios[x]) > ceiling:
            remove_these.append(x)
    if len(remove_these) > 0:
        limited_ratios = []
        limited_new_timestamps = []
        remove_these.reverse()
        for y in remove_these:
            if ratios[y] > 0:
                limited_ratios.append(ceiling)
            else:
                limited_ratios.append(-ceiling)
            limited_new_timestamps.append(new_timestamps[y])
            ratios.remove(ratios[y])
            new_timestamps.remove(new_timestamps[y])
        #
        print('ceiling busted!')
        ceiling_busted(name, new_timestamps, limited_new_timestamps, ratios, limited_ratios, width, height, corrects, incorrects, directory, table)
    else:
        print('not busted')
        not_busted(name, new_timestamps, ratios, width, height, corrects, incorrects, directory, table)


def ceiling_busted(name, timestamps, limited_timestamps, ratio, limited_ratio, width, height, corrects, incorrects, directory, table=None):
    plt.figure(figsize=(width,height))
    plt.suptitle(name)
    plt.plot(timestamps, ratio, color='black')
    plt.scatter(limited_timestamps, limited_ratio, color='red')
    plt.xlabel('Time')
    plt.ylabel('Power?')
    if table is not None:
        for a in corrects:
            plt.axvline(x=a, color='purple')
        for b in incorrects:
            plt.axvline(x=b, color='orange')
    
    plt.savefig(name)
    plt.close()


def not_busted(name, timestamps, ratio, width, height, corrects, incorrects, directory, table=None):
    plt.figure(figsize=(width,height))
    plt.suptitle(name)
    plt.plot(timestamps, ratio, color='black')
    plt.xlabel('Time')
    plt.ylabel('Power?')
    if table is not None:
        for a in corrects:
            plt.axvline(x=a, color='purple')
        for b in incorrects:
            plt.axvline(x=b, color='orange')
    
    plt.savefig(name)
    plt.close()


def main(filepath, ceiling):
    directory = os.path.dirname(os.path.abspath(filepath))
    with open(filepath, 'rb') as f:
        data = pickle.load(f)

    timestamps = []
    for x in range(len(data)):
        for y in data[x].keys():
            timestamps.append(y)

    db = sqlite3.Connection('db.sqlite')
    curs = db.cursor()
    tables = curs.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()[2:]
    tables = [x[0] for x in tables]
    for x in tables:
        start_time = curs.execute('SELECT MIN(Timestamp) FROM ' + x + ';').fetchall()[0][0]
        if start_time > timestamps[0] and start_time < timestamps[-1]:
            table = x
            break
    try:
        print('Using table: ' + table)
    except NameError:
        print('Could not find a table with timestamps matching EEG data.')
        table = None
        curs.close()
        db.close()
    
    os.chdir(os.path.dirname(filepath))

    deltas = []
    thetas = []
    alphas = []
    betas = []
    gammas = []

    for x in range(len(data)):
        for y in data[x].values():
            for z in range(len(y[0])):
                if z == 0:
                    deltas.append(y[0][z])
                elif z == 1:
                    thetas.append(y[0][z])
                elif z == 2:
                    alphas.append(y[0][z])
                elif z == 3:
                    betas.append(y[0][z])
                elif z == 4:
                    gammas.append(y[0][z])

    smooth_deltas = []
    smooth_thetas = []
    smooth_alphas = []
    smooth_betas = []
    smooth_gammas = []

    for x in range(len(data)):
        for y in data[x].values():
            for z in range(len(y[1])):
                if z == 0:
                    smooth_deltas.append(y[1][z])
                elif z == 1:
                    smooth_thetas.append(y[1][z])
                elif z == 2:
                    smooth_alphas.append(y[1][z])
                elif z == 3:
                    smooth_betas.append(y[1][z])
                elif z == 4:
                    smooth_gammas.append(y[1][z])

    """
    # am i going to use these?
    delta_abs = [abs(x) for x in deltas]
    theta_abs = [abs(x) for x in thetas]
    alpha_abs = [abs(x) for x in alphas]
    beta_abs = [abs(x) for x in betas]
    gamma_abs = [abs(x) for x in gammas]

    sm_delta_abs = [abs(x) for x in smooth_deltas]
    sm_theta_abs = [abs(x) for x in smooth_thetas]
    sm_alpha_abs = [abs(x) for x in smooth_alphas]
    sm_beta_abs = [abs(x) for x in smooth_betas]
    sm_gamma_abs = [abs(x) for x in smooth_gammas]
    """

    # Alpha Protocol:
    # Simple redout of alpha power, divided by delta waves in order to rule out noise
    alpha_over_delta = []
    # Beta Protocol:
    # Beta waves have been used as a measure of mental activity and concentration
    # This beta over theta ratio is commonly used as neurofeedback for ADHD
    beta_over_theta = []
    # Alpha/Theta Protocol:
    # This is another popular neurofeedback metric for stress reduction
    # Higher theta over alpha is supposedly associated with reduced anxiety
    theta_over_alpha = []
    # Gamma/Beta:
    # I suspect this may indicate when a person's intuition is at its strongest.
    # Gamma waves have been associated with psi phenomena by multiple other researchers.
    # Beta brainwaves are associated with analytical thinking, which is widely believed to inhibit psi.
    gamma_over_beta = []
    # here we go!
    for x in range(len(smooth_deltas)):
        alpha_over_delta.append(smooth_alphas[x] / smooth_deltas[x])
        beta_over_theta.append(smooth_betas[x] / smooth_thetas[x])
        theta_over_alpha.append(smooth_thetas[x] / smooth_alphas[x])
        gamma_over_beta.append(smooth_gammas[x] / smooth_betas[x])

    if table is not None:
        corrects = curs.execute('select timestamp from ' + table + ' where Correct=1;').fetchall()
        incorrects = curs.execute('select timestamp from ' + table + ' where Correct=0;').fetchall()

    width = len(timestamps) // 5
    height = width // 5
    
    universal_args = [timestamps, width, height, corrects, incorrects, directory, table]

    p0 = Process(target=power_plot, args=('deltas', deltas, *universal_args))
    p1 = Process(target=power_plot, args=('thetas', thetas, *universal_args))
    p2 = Process(target=power_plot, args=('alphas', alphas, *universal_args))
    p3 = Process(target=power_plot, args=('betas', betas, *universal_args))
    p4 = Process(target=power_plot, args=('gammas', gammas, *universal_args))

    p5 = Process(target=power_plot, args=('smooth_deltas', smooth_deltas, *universal_args))
    p6 = Process(target=power_plot, args=('smooth_thetas', smooth_thetas, *universal_args))
    p7 = Process(target=power_plot, args=('smooth_alphas', smooth_alphas, *universal_args))
    p8 = Process(target=power_plot, args=('smooth_betas', smooth_betas, *universal_args))
    p9 = Process(target=power_plot, args=('smooth_gammas', smooth_gammas, *universal_args))

    prefix = str(ceiling)
    p10 = Process(target=ratio_plot, args=(prefix + '_alpha_over_delta', alpha_over_delta, ceiling, *universal_args))
    p11 = Process(target=ratio_plot, args=(prefix + '_beta_over_theta', beta_over_theta, ceiling, *universal_args))
    p12 = Process(target=ratio_plot, args=(prefix + '_theta_over_alpha', theta_over_alpha, ceiling, *universal_args))
    p13 = Process(target=ratio_plot, args=(prefix + '_gamma_over_beta', gamma_over_beta, ceiling, *universal_args))
    
    """
    the point here is to reduce RAM use,
    which can get pretty out of hand if
    these aren't spawned in their own sub-processes
    and run one at a time
    """
    processes = [p0, p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13]
    for p in processes:
        p.start()
        p.join()
    
    try:
        curs.close()
        db.close()
    except Exception:
        pass


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('filepath', nargs='?', default=None)
    parser.add_argument('-c', '--ceiling', nargs='?', type=int, default=2)
    args = parser.parse_args()

    if args.filepath == None or not os.path.isfile(args.filepath):
        filepath = input('Enter the full (absolute or relative) filepath to the pickled neurofeedback file you wish to analyze:\n')
    else:
        filepath = args.filepath
    
    main(filepath, args.ceiling)