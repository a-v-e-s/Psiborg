import os, pickle, sqlite3
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter.filedialog import askopenfilename
from threading import Thread
from multiprocessing import cpu_count
from time import sleep


def power_plot(name, values, timestamps, width, height, corrects, incorrects, savefigs, directory, table=None):    
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
    if savefigs == True:
        plt.save(os.path.join(directory, name))
    else:
        plt.show()


def ratio_plot(name, ratios, ceiling, timestamps, width, height, corrects, incorrects, savefigs, directory, table=None):
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
        ceiling_busted(name, new_timestamps, limited_new_timestamps, ratios, limited_ratios, width, height, corrects, incorrects, savefigs, directory, table)
    else:
        print('not busted')
        not_busted(name, new_timestamps, ratios, width, height, corrects, incorrects, savefigs, directory, table)


def ceiling_busted(name, timestamps, limited_timestamps, ratio, limited_ratio, width, height, corrects, incorrects, savefigs, directory, table=None):
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
    if savefigs == True:
        plt.save(os.path.join(directory, name))
    else:
        plt.show()


def not_busted(name, timestamps, ratio, width, height, corrects, incorrects, savefigs, directory, table=None):
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
    if savefigs == True:
        plt.save(os.path.join(directory, name))
    else:
        plt.show()


def main():
    filename = askopenfilename()
    directory = os.path.dirname(filename)
    with open(filename, 'rb') as f:
        data = pickle.load(f)

    # when i get all of this straightened out...
    if input('Save plotted figures? [y/n]').lower() == 'y':
        savefigs = True
    else:
        savefigs = False

    try:
        ceiling = int(input('Set ceiling for busted ratio graphs: (pick an integer)'))
    except ValueError:
        print('Invalid input. Setting ceiling = 2')
        ceiling = 2

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
    
    os.chdir(os.path.dirname(filename))

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
    
    universal_args = [timestamps, width, height, corrects, incorrects, savefigs, directory, table]

    t0 = Thread(target=power_plot, args=('deltas', deltas, *universal_args))
    t1 = Thread(target=power_plot, args=('thetas', thetas, *universal_args))
    t2 = Thread(target=power_plot, args=('alphas', alphas, *universal_args))
    t3 = Thread(target=power_plot, args=('betas', betas,  *universal_args))
    t4 = Thread(target=power_plot, args=('gammas', gammas, *universal_args))

    t5 = Thread(target=power_plot, args=('smooth_deltas', smooth_deltas, *universal_args))
    t6 = Thread(target=power_plot, args=('smooth_thetas', smooth_thetas, *universal_args))
    t7 = Thread(target=power_plot, args=('smooth_alphas', smooth_alphas, *universal_args))
    t8 = Thread(target=power_plot, args=('smooth_betas', smooth_betas, *universal_args))
    t9 = Thread(target=power_plot, args=('smooth_gammas', smooth_gammas, *universal_args))

    t10 = Thread(target=ratio_plot, args=('alpha_over_delta', alpha_over_delta, ceiling, *universal_args))
    t12 = Thread(target=ratio_plot, args=('beta_over_theta', beta_over_theta, ceiling, *universal_args))
    t13 = Thread(target=ratio_plot, args=('theta_over_alpha', theta_over_alpha, ceiling, *universal_args))
    t14 = Thread(target=ratio_plot, args=('gamma_over_beta', gamma_over_beta, ceiling, *universal_args))

    thread_pool = [t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14]
    
    if cpu_count >= 3:
        processors = cpu_count() - 1
    else:
        processors = 1

    running_threads = []
    for x in range(processors-1):
        try:
            thread_pool[x].start()
            running_threads.append(thread_pool[x])
            thread_pool.remove(thread_pool[x])
        except IndexError:
            break
    
    while thread_pool:
        sleep(1)
        for x in running_threads:
            if not x.is_alive():
                running_threads.remove(x)
                thread_pool[0].start()
                running_threads.append(thread_pool[0])
                thread_pool.remove(thread_pool[0])
                break
    for x in running_threads:
        x.join()
    
    try:
        curs.close()
        db.close()
    except Exception:
        pass


if __name__ == '__main__':
    main()