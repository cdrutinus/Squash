#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


def f(rank):
    return 1/np.sqrt(rank)


# In[3]:


def calcul_classement(df, f, calc_sets=False):
    
    n_joueurs = len(df.Joueurs.unique())
    
    ### Résultat de chaque match
    résultats = []
    for match in df.Match.unique():
        scores = list(df[df["Match"]==match]["Scores"])
        
        résultat = -1
        if scores[0] > scores[1]:
            résultat = 1
        elif scores[0] == scores[1]:
            résultat = 0
            
        résultats.append(résultat)
        résultats.append(-résultat)

    df["Résultat"] = résultats

    ### Points de chaque match
    points = []
    for match in df.Match.unique():
        classement = list(df[df["Match"]==match]["Classement"])        
        sets = list(df[df["Match"]==match]["Scores"])
        résultat = list(df[df["Match"]==match]["Résultat"])
        for i in range(2):
            if calc_sets==False:
                point = max(3*np.sqrt(n_joueurs)*résultat[i]*f(classement[1-i]), 0)
                points.append(point) 
            else:
                point = sets[i]*f(classement[1-i]) + (résultat[i]+1)
                points.append(point)
                
        
    df["Points"] = points
    
    ### Calcul des stats de chaque joueur
    df_rang = pd.DataFrame(columns={"Joueur"})
    
    df_rang["Joueur"] = df.Joueurs.unique()
    joués, victoires, nuls, défaites, taux, points_joueurs = [], [], [], [], [], []
    for joueur in df_rang["Joueur"]:
        nb_joués = df[df["Joueurs"]==joueur].shape[0]
        joués.append(nb_joués)
        nb_victoires = list(df[df["Joueurs"]==joueur]["Résultat"]).count(1)
        victoires.append(nb_victoires)
        nb_nuls = list(df[df["Joueurs"]==joueur]["Résultat"]).count(0)
        nuls.append(nb_nuls)
        nb_défaites = list(df[df["Joueurs"]==joueur]["Résultat"]).count(-1)
        défaites.append(nb_défaites)
        taux.append("{}%".format(int(nb_victoires/nb_joués*100)))
        points_joueurs.append(round(sum(list(df[df["Joueurs"]==joueur]["Points"])), 2))

    df_rang["Joués"] = joués
    df_rang["Victoires"] = victoires
    df_rang["Nuls"] = nuls
    df_rang["Défaites"] = défaites
    df_rang["Taux de succès"] = taux
    df_rang["Points"] = points_joueurs

    df_rang.sort_values(by=["Points", "Taux de succès"], ascending=[False, False], inplace=True)
    
    df_rang["Rang"] = range(1, n_joueurs+1)
    
    return df_rang


# In[4]:


def classement_squash(filename, f, calc_sets):
    
    df_matchs = pd.read_csv(filename, sep=';', decimal=',')
    
    if df_matchs.Classement.isna().any():
                
        df_previous_matchs = df_matchs.dropna().copy()

        df_previous_rank = calcul_classement(df_previous_matchs, f, calc_sets)

        # Remplissage avec les nouveaux classements
        for i in range(df_matchs.shape[0]):
            if np.isnan(df_matchs["Classement"][i]):
                joueur = df_matchs["Joueurs"][i]
                df_matchs["Classement"][i] = df_previous_rank[df_previous_rank["Joueur"]==joueur]["Rang"]

        # Export de l'historique mis à jour
        df_matchs.to_csv(filename, sep=';', decimal=',', columns=["Match", "Joueurs", "Classement", "Scores"], index=False)
    
    # Classement final
    df_rank = calcul_classement(df_matchs, f, calc_sets)
    
    return df_rank


# In[6]:


rank = classement_squash("Historique.csv", f, True)
print(rank.to_string(index=False))


# In[7]:


df_attribution_points = pd.DataFrame(columns={"Joueur", "Points à gagner (sur un set)"})
df_attribution_points["Joueur"] = rank.Joueur
n_joueurs = len(list(df_attribution_points["Joueur"]))
df_attribution_points["Points à gagner (sur un set)"] = [f(i) for i in range(1, n_joueurs + 1)]
df_attribution_points["Points à gagner (sur un match)"] = df_attribution_points["Points à gagner (sur un set)"]*3 + 2

print(df_attribution_points.to_string(index=False))


# In[ ]:




