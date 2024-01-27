import tkinter as tk
from tkinter import ttk
import csv
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Can2024App:
    def __init__(self, root):
        self.root = root
        self.root.title("CAN 2024 - Statistiques et Prévisions")
        self.root.geometry("1100x700")

        # En-tête
        self.header_frame = tk.Frame(root, bg='blue', padx=10, pady=10)
        self.header_frame.pack(side='top', fill='x')

        self.title_label = tk.Label(self.header_frame, text="CAN 2024", font=('Helvetica', 18), fg='white', bg='blue')
        self.title_label.pack()

        self.subtitle_label = tk.Label(self.header_frame, text="Statistiques, Analyses et Prévisions", font=('Helvetica', 10), fg='white', bg='blue')
        self.subtitle_label.pack()

        # Barre latérale
        self.sidebar = tk.Frame(root, width=200, bg='gray')
        self.sidebar.pack(side='left', fill='y')

        # Notebook pour contenir les pages
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(side='right', fill='both', expand=True)

        # Créer une page pour l'accueil
        self.home_page = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.home_page)

        # Créer une page pour les statistiques
        self.stats_page = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.stats_page)

        # Créer une page pour les prévisions
        self.predictions_page = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.predictions_page)

        # Ajouter des boutons à la barre latérale
        self.home_button = ttk.Button(self.sidebar, text="Accueil", command=self.show_home)
        self.home_button.pack(pady=10, padx=5, fill='x')

        self.stats_button = ttk.Button(self.sidebar, text="Statistiques", command=self.show_stats)
        self.stats_button.pack(pady=10, padx=5, fill='x')

        self.predictions_button = ttk.Button(self.sidebar, text="Prévisions", command=self.show_predictions)
        self.predictions_button.pack(pady=10, padx=5, fill='x')

        # Afficher l'accueil par défaut
        self.show_home()

    def show_home(self):
        # Supprimer tout contenu existant dans la page "Accueil"
        for widget in self.home_page.winfo_children():
            widget.destroy()

        # Charger les données depuis le fichier equipes.csv
        groups_data = self.load_groups_data()

        # Définir le nombre de colonnes souhaité
        cols = 3

        # Configurer la proportion des lignes et des colonnes
        for i in range(cols):
            self.home_page.columnconfigure(i, weight=1)  # Chaque colonne a le même poids

        total_rows = len(groups_data)
        for i in range(total_rows):
            # Ajuster la proportion de chaque ligne en fonction de vos besoins
            self.home_page.rowconfigure(i, weight=1)

        # Afficher les groupes dans la page "Accueil" du notebook
        for i, (group, teams) in enumerate(groups_data.items()):
            group_frame = tk.Frame(self.home_page, bg=None, pady=10)
            group_frame.grid(row=i // cols, column=i % cols, padx=10, pady=10, sticky='nsew')

            group_label = tk.Label(group_frame, text=f"Groupe {group}", font=('Helvetica', 14), pady=5)
            group_label.pack()

            for team_info in teams:
                team_label = tk.Label(group_frame, text=team_info['Name'], font=('Helvetica', 12), pady=2, cursor='hand2', fg='blue')
                team_label.pack()
                team_label.bind("<Button-1>", lambda event, team_info=team_info: self.team_info(team_info))

        # Mettre à jour le notebook pour afficher la page "Accueil"
        self.notebook.select(self.home_page)

    def load_groups_data(self):
        # Charger les données depuis le fichier equipes.csv
        groups_data = {}
        with open('assets/datas/equipes_can2024.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                group = row['Groupe']
                team_name = row['Équipe']
                team_code = row['Code']

                team_info = {'Name': team_name, 'Code': team_code}

                if group in groups_data:
                    groups_data[group].append(team_info)
                else:
                    groups_data[group] = [team_info]

        return groups_data

    def team_info(self, team_info):
        # Fermer toutes les fenêtres pop-up précédemment ouvertes
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()

        # Création de la fenêtre pop-up
        popup = tk.Toplevel(self.root)
        popup.title(f"Informations sur {team_info['Name']} ({team_info['Code']})")

        # Ajout du titre principal (h1)
        main_title_label = tk.Label(popup, text=f"{team_info['Name']} ({team_info['Code']})", font=('Helvetica', 16, 'bold'), pady=10)
        main_title_label.grid(row=0, column=0, columnspan=2)

        # Frame pour les deux blocs à gauche
        left_frame = tk.Frame(popup)
        left_frame.grid(row=1, column=0, pady=10, padx=20, sticky='nsew')

        # Bloc 1: Classements de l'équipe
        rankings_frame = tk.Frame(left_frame)
        rankings_frame.pack(pady=10)

        # Titre du bloc 1
        rankings_title_label = tk.Label(rankings_frame, text="Informations Générales", font=('Helvetica', 14, 'underline'), pady=5)
        rankings_title_label.pack()

        # Chargement des données du classement FIFA
        fifa_ranking_data = self.load_fifa_ranking_data()

        # Nom de l'équipe actuelle
        current_team_name = team_info['Name']
        # Charger les données des joueurs depuis le fichier correspondant
        players_data = self.load_players_data(team_info['Code'].lower())

        # Charger les données du classement mondial des clubs
        club_classement_mondial = pd.read_csv('assets/datas/clubs/club_classement_mondial.csv')

        # Calculer la qualité de l'équipe
        team_quality_points = 0

        # Parcourir les joueurs de l'équipe
        for player_info in players_data:
            player_club = player_info['Club']

            # Vérifier si le club du joueur est dans le fichier de classement des clubs
            if player_club in club_classement_mondial['Club'].tolist():
                # Récupérer les points du club dans le fichier de classement des clubs
                club_points = club_classement_mondial.loc[club_classement_mondial['Club'] == player_club, 'Points'].values[0]
                # Ajouter les points du club à la qualité de l'équipe
                team_quality_points += club_points

        # Affichage de la qualité de l'équipe
        team_quality_label = tk.Label(rankings_frame, text=f"Qualité de l'équipe : {team_quality_points} points", font=('Helvetica', 12))
        team_quality_label.pack()

        # Affichage du classement FIFA pour l'équipe actuelle
        for ranking_info in fifa_ranking_data:
            if ranking_info['Pays'] == current_team_name:
                ranking_label = tk.Label(rankings_frame, text=f"Classement FIFA : {ranking_info['Pays']} : {ranking_info['Classement']}e", font=('Helvetica', 12))
                ranking_label.pack()


        # Frame pour le tableau à droite
        right_frame = tk.Frame(popup)
        right_frame.grid(row=1, column=1, pady=10, padx=20, sticky='nsew')

        # Charger les données des joueurs depuis le fichier correspondant
        players_data = self.load_players_data(team_info['Code'].lower())

        # Créer un Treeview pour afficher les joueurs
        tree = ttk.Treeview(right_frame, columns=('Code', 'Nom', 'Position', 'Club'), height=30, show='headings')
        tree.heading('Code', text='Code')
        tree.heading('Nom', text='Nom du Joueur')
        tree.heading('Position', text='Position')
        tree.heading('Club', text='Club')

        # Ordonner les joueurs des gardiens aux attaquants
        sorted_players = sorted(players_data, key=lambda x: self.position_weight(x['Position']))

        # Remplir le Treeview avec les données des joueurs
        for player in sorted_players:
            tree.insert('', 'end', values=(player['Code'], player['Nom'], player['Position'], player['Club']))

        tree.pack()

    def load_fifa_ranking_data(self):
        # Charger les données depuis le fichier fifa_rang_afrique.csv
        fifa_ranking_data = []
        with open('assets/datas/fifa/fifa_rang_mondial.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                fifa_ranking_data.append(row)

        return fifa_ranking_data

    def position_weight(self, position):
        # Fonction de mapping pour attribuer un poids à chaque position
        positions = {'Gardien': 1, 'Défenseur': 2, 'Milieu': 3, 'Attaquant': 4}
        return positions.get(position, 0)

    def load_players_data(self, code_name):
        # Charger les données des joueurs depuis le fichier CSV
        players_data = []
        file_path = f"assets/datas/nations/{code_name.lower()}.csv"

        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    players_data.append({
                        'Code': row['Code'],
                        'Nom': row['Nom du Joueur'],
                        'Position': row['Position'],
                        'Club': row['Club']
                    })
        except FileNotFoundError:
            print(f"Le fichier {file_path} n'a pas été trouvé.")

        return players_data

    def show_stats(self):
        # Supprimer tout contenu existant dans la page "Statistiques"
        for widget in self.stats_page.winfo_children():
            widget.destroy()

        # Chargez les données depuis les fichiers CSV
        equipes_can2024 = pd.read_csv('assets/datas/equipes_can2024.csv')
        fifa_rang_mondial = pd.read_csv('assets/datas/fifa/fifa_rang_mondial.csv')

        # Fusionnez les deux DataFrames sur la colonne "Équipe" (équipes_can2024) et "Pays" (fifa_rang_mondial)
        merged_data = pd.merge(equipes_can2024, fifa_rang_mondial, left_on='Équipe', right_on='Pays')

        # Triez les données en fonction du classement FIFA
        sorted_data = merged_data.sort_values(by='Classement')

        # Créez un diagramme de comparaison
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(sorted_data['Équipe'], sorted_data['Points'], color='blue')
        ax.set_xlabel('Équipe')
        ax.set_ylabel('Classement FIFA (Points)')
        ax.set_title('Comparaison selon le Classement FIFA des Équipes de la CAN 2024')

        # Ajoutez cette ligne pour définir les positions des ticks sur l'axe x
        ax.set_xticks(range(len(sorted_data['Équipe'])))
        ax.set_xticklabels(sorted_data['Équipe'], rotation=45, ha='right')

        # Créez un objet FigureCanvasTkAgg pour afficher le graphique dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.stats_page)
        canvas.draw()

        # Affichez le graphique dans le widget Tkinter
        canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')

        # Mettez à jour le notebook pour afficher la page "Statistiques"
        self.notebook.select(self.stats_page)

    def show_predictions(self):
        # Supprimer tout contenu existant dans la page "Prévisions"
        for widget in self.predictions_page.winfo_children():
            widget.destroy()

        # Ajoutez le code pour afficher les prévisions dans la page "Prévisions"
        # Remplacez cela par votre logique spécifique pour les prévisions
        predictions_label = tk.Label(self.predictions_page, text="Prévisions à venir...", font=('Helvetica', 16), pady=20)
        predictions_label.pack()

        # Mettez à jour le notebook pour afficher la page "Prévisions"
        self.notebook.select(self.predictions_page)


if __name__ == "__main__":
    root = tk.Tk()
    app = Can2024App(root)
    root.mainloop()
