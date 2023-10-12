import tkinter as tk
from tkinter import ttk, messagebox

import smtplib
import random
import os
from email.mime.text import MIMEText
from colorama import init, Fore
import time
import sys 
init(autoreset=True)

# need to implement: Optional: allow user to predetermine more than one traitors

def weighted_shuffle_first(orig_list, favored_element, favored_weight, num):
    """
    Easiest way to increase the chance that the selected role is shuffled 
    to the first of the role list. Not statistically rigorous, but strong
    enough for this naive role_assigning execution
    
    orig_list: original list to shuffle
    favored_element: element that has a higher chance to be placed first
    favored_weight: the weight for the favored element.
    """
    # ensure the favored_element is in orig_list
    assert favored_element in orig_list, f"{favored_element} not found in original list"
    
    # temporarily add extra copies of the favored_element
    augmented_list = orig_list + [favored_element] * (favored_weight - 1)
    random.shuffle(augmented_list)
    
    # remove extra copies
    while augmented_list.count(favored_element) > num:
        augmented_list.remove(favored_element)
    
    return augmented_list

# only call each function once during the execution, hence modifying the reference is acceptable
# If the global vars 'group', 'role', 'pos' should remain the same, copy params to local vars in funcs.
def send_roles_with_positions(group1, group2, roles1, roles2, pos, posTypeNum,
                              predetermined = False, traitor_email = 'not_exist', favored_weight = 10, uniqueness = True):
    """
    Assign roles and positions to two groups and send email notifications.

    This function is designed to shuffle and assign roles and positions to 
    members of two groups, and subsequently send email notifications to inform 
    them of their assignments. The assigned position can be repetitive.
    An option to predetermine the assignment of the "traitor" role is available. 
    If true, the player with "traitor_email" will be more likely to be assigned 
    the "traitor" role.

    Parameters:
    - group1, group2 (list of str): The email addresses of members in each group.
    - roles1, roles2 (list of str): The roles to be assigned to the members of each group.
    - pos (list of str): The positions to be assigned to members.
    - posTypeNum (int): the number of types of positions.
    - predetermined (bool, optional): If True, enables the assignment of the 
                                      "traitor" role to the email address specified 
                                      in `traitor_email`. Defaults to False.
    - traitor_email (str, optional): The email address of the member to be 
                                     assigned the "traitor" role if `predetermined` 
                                     is True. Defaults to 'not_exist'.
    - favored_weight (int, optional): The weight favoring the "traitor" role 
                                      assignment in shuffling when `predetermined` 
                                      is True. Defaults to 10.
    - uniqueness (bool, optional): If True, ensures the positions assigned are 
                                   unique to each member. Defaults to True.

    Returns:
    None

    Note:
    1. The email server connection (`server`) and email sender address (`email_address`)
    are assumed to be pre-configured and available in the function's scope. 
    2. Position list should be at least at the same length with any player group to be
    assigned a position properly.
    3. Designated traitor player must be placed at the first in "group" list to be more
    likely assigned a "traitor" role.
    
    Example Usage:
    >>> group1 = ['alice@email.com', 'bob@email.com']
    >>> group2 = ['charlie@email.com', 'dave@email.com']
    >>> roles1 = ['traitor', 'good']
    >>> roles2 = ['traitor', 'good']
    >>> pos = ['pos1', 'pos2', 'pos3', 'pos4', 'pos5']
    >>> send_roles_with_positions(group1, group2, roles1, roles2, pos,
                                  predetermined=True, traitor_email='alice@email.com',
                                  favored_weight=5, uniqueness=True)
    """
    # condition check
    if len(roles1) != len(group1) or len(roles2) != len(group2):
        print("Number of players is not equal to number of roles")
        return
    
    # Shuffling the roles to assign them randomly
    if (not predetermined):
        print("Assigning not predetermined roles...")
        random.shuffle(roles1)
        random.shuffle(roles2)
    else:
        if (traitor_email == 'not_exist'):
            print("The traitor_email parameter is not assigned!")
            return
        
        print("Assigning predetermined roles...")
        traitor1_num = roles1.count("traitor")
        traitor2_num = roles2.count("traitor")
        # we assume that traitor's name must be in either group1 or group2. No cornor case check
        traitor_in_group1 = False
        for email in group1:
            if traitor_email == email:
                traitor_in_group1 = True
        if (traitor_in_group1):
            weighted_shuffle_first(roles1, "traitor", favored_weight, traitor1_num)
            random.shuffle(roles2)
        else:
            weighted_shuffle_first(roles2, "traitor", favored_weight, traitor2_num)
            random.shuffle(roles1)
            
    # determine if positions are unique 
    if len(pos) < len(group1) or len(pos) < len(group2):
        print("Position list should be at least at the same length with "
              + "any player group to be assigned a position properly.")
    if (uniqueness):
        print("Assigning unique positions...")
        pos = pos[:posTypeNum] 
    else: 
        print("Assigning positions (may be repeated)...")
    
    # Shuffle positions for group1
    pos_group1 = pos.copy()
    random.shuffle(pos_group1)
    
    # Shuffle positions for group2
    pos_group2 = pos.copy()
    random.shuffle(pos_group2)
    
    # Sending email to each person with their role
    for i in range(len(group1)):
        # Use pos_group1 for group1
        msg = MIMEText(f'Your role is: {roles1[i]}, your position is {pos_group1[i]}\n Roles are either \"traitor\" or \"good\".')
        msg['From'] = email_address
        msg['To'] = group1[i]
        msg['Subject'] = 'Your Role Information: ' + roles1[i]
        
        # for testing purpose
        # print(group1[i] + ': ' + roles1[i] + ", " + pos[i])
        
        # comment following area only if testing
        try:
            server.sendmail(email_address, [group1[i]], msg.as_string())
            print(f"Email sent to {group1[i]} successfully.")
        except Exception as e:
            print(f"Failed to send email to {group1[i]}. Error: {str(e)}")
            
    for i in range(len(group2)):
        # Use pos_group2 for group2
        msg = MIMEText(f'Your role is: {roles2[i]}, your position is {pos_group2[i]}\n Roles are either \"traitor\" or \"good\".')
        msg['From'] = email_address
        msg['To'] = group2[i]
        msg['Subject'] = 'Your Role Information: ' + roles2[i]

        # for testing purpose
        # print(group2[i] + ': ' + roles2[i] + ", " + pos[i])
        
        # comment following area only if testing
        try:
            server.sendmail(email_address, [group2[i]], msg.as_string())
            print(f"Email sent to {group2[i]} successfully.")
        except Exception as e:
            print(f"Failed to send email to {group2[i]}. Error: {str(e)}")
            
def send_roles(group1, group2, roles1, roles2,
               predetermined = False, traitor_email = 'not_exist', favored_weight = 10):
    """
    Assign roles to two groups and send email notifications.

    This function is designed to shuffle and assign roles to 
    members of two groups, and subsequently send email notifications to inform 
    them of their assignments. An option to predetermine the assignment of the 
    "traitor" role is available. If true, the player with "traitor_email" will
    be more likely to be assigned the "traitor" role.

    Parameters:
    - group1, group2 (list of str): The email addresses of members in each group.
    - roles1, roles2 (list of str): The roles to be assigned to the members of each group.
    - predetermined (bool, optional): If True, enables the assignment of the 
                                      "traitor" role to the email address specified 
                                      in `traitor_email`. Defaults to False.
    - traitor_email (str, optional): The email address of the member to be 
                                     assigned the "traitor" role if `predetermined` 
                                     is True. Defaults to 'not_exist'.
    - favored_weight (int, optional): The weight favoring the "traitor" role 
                                      assignment in shuffling when `predetermined` 
                                      is True. Defaults to 10.

    Returns:
    None

    Note:
    1. The email server connection (`server`) and email sender address (`email_address`)
    are assumed to be pre-configured and available in the function's scope.
    2. Designated traitor player must be placed at the first in "group" list to be more
    likely assigned a "traitor" role.
    
    Example Usage:
    >>> group1 = ['alice@email.com', 'bob@email.com']
    >>> group2 = ['charlie@email.com', 'dave@email.com']
    >>> roles1 = ['traitor', 'good']
    >>> roles2 = ['traitor', 'good']
    >>> send_roles_with_positions(group1, group2, roles1, roles2, predetermined=True, 
                                    traitor_email='alice@email.com', favored_weight=5)
    """
    # condition check
    if len(roles1) != len(group1) or len(roles2) != len(group2):
        print("Number of players is not equal to number of roles")
        return
        
    # Shuffling the roles to assign them randomly
    if (not predetermined):
        print("Assigning not predetermined roles...")
        random.shuffle(roles1)
        random.shuffle(roles2)
    else:
        if (traitor_email == 'not_exist'):
            print("The traitor_email parameter is not assigned!")
            return
        
        print("Assigning predetermined roles...")
        traitor1_num = roles1.count("traitor")
        traitor2_num = roles2.count("traitor")
        # we assume that traitor's name must be in either group1 or group2. No cornor case check
        traitor_in_group1 = False
        for email in group1:
            if traitor_email == email:
                traitor_in_group1 = True
        if (traitor_in_group1):
            weighted_shuffle_first(roles1, "traitor", favored_weight, traitor1_num)
            random.shuffle(roles2)
        else:
            weighted_shuffle_first(roles2, "traitor", favored_weight, traitor2_num)
            random.shuffle(roles1)
    
    # Sending email to each person with their role
    for i in range(len(group1)):
        msg = MIMEText(f'Your role is: {roles1[i]}\n Roles are either \"traitor\" or \"good\".')
        msg['From'] = email_address
        msg['To'] = group1[i]
        msg['Subject'] = 'Your Role Information: ' + roles1[i]
        
        # for testing purpose
        # print(group1[i] + ': ' + roles1[i])
        
        # comment following area only if testing
        try:
            server.sendmail(email_address, [group1[i]], msg.as_string())
            print(f"Email sent to {group1[i]} successfully.")
        except Exception as e:
            print(f"Failed to send email to {group1[i]}. Error: {str(e)}")
            
    for i in range(len(group2)):
        msg = MIMEText(f'Your role is: {roles2[i]}\n Roles are either \"traitor\" or \"good\".')
        msg['From'] = email_address
        msg['To'] = group2[i]
        msg['Subject'] = 'Your Role Information: ' + roles2[i]
        
        # for testing purpose
        # print(group2[i] + ': ' + roles2[i])

        # comment following area only if testing
        try:
            server.sendmail(email_address, [group2[i]], msg.as_string())
            print(f"Email sent to {group2[i]} successfully.")
        except Exception as e:
            print(f"Failed to send email to {group2[i]}. Error: {str(e)}")

def yn_check(input):
    if input in ['y', 'n']:
        return True
    else:
        print(Fore.RED + "Invalid input. Please enter y or n.")
        return False

def select_names_from_list(num_people, available_names):
    group = []

    i = 0
    while i < num_people:
        print(Fore.CYAN + f"Available names: {', '.join(available_names)}")
        name = input(Fore.YELLOW + f"Select name for person {i+1}: ").strip().upper()
        
        if name in available_names:
            group.append(emails[name])
            available_names.remove(name)
            i += 1  # Increment the counter only if the selection was valid
        else:
            print(Fore.RED + f"Name '{name}' is not in the available list. Please choose from the list.")
            # No need for the decrement operation; just let the loop repeat
    
    return group

def modify_positions_list(positions):
    while True:
        print(Fore.CYAN + "\nCurrent positions: " + ", ".join(positions))
        print(Fore.YELLOW + "\nOptions:")
        print("1. Add a position")
        print("2. Remove a position")
        print("3. Exit")
        
        choice = input(Fore.GREEN + "\nEnter your choice (1/2/3): ")
        
        if choice == "1":
            new_position = input(Fore.YELLOW + "\nEnter the name of the position to add: ").strip()
            if new_position in positions:
                print(Fore.RED + f"Position '{new_position}' already exists!")
            else:
                positions.append(new_position)
                print(Fore.GREEN + f"Position '{new_position}' added successfully!")
                
        elif choice == "2":
            remove_position = input(Fore.YELLOW + "\nEnter the name of the position to remove: ").strip()
            if remove_position not in positions:
                print(Fore.RED + f"Position '{remove_position}' doesn't exist!")
            else:
                positions.remove(remove_position)
                print(Fore.GREEN + f"Position '{remove_position}' removed successfully!")
                
        elif choice == "3":
            break
        else:
            print(Fore.RED + "Invalid choice. Please select 1, 2, or 3.")
    
    return positions

def create_roles_list(num_people, num_traitors):
    roles = ['traitor'] * num_traitors + ['good'] * (num_people - num_traitors)
    random.shuffle(roles)
    return roles

def load_emails_from_file(filename):
    emails = {}
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            for line in file.readlines():
                name, email = line.strip().split(',')
                emails[name] = email
    else:
        print(Fore.RED + f"'{filename}' does not exist. Starting with an empty email list.")
    return emails

def send_teams(team_selections, traitor_team1_spin, traitor_team2_spin, randomized_var, unique_var):
    team1 = []
    team2 = []
    
    # Loop through the team_selections to gather selected teams
    for name, team1_var, team2_var in team_selections:
        if team1_var.get() == 1:
            team1.append(emails[name])
        elif team2_var.get() == 1:
            team2.append(emails[name])

    # Get number of traitors from spinboxes
    try:
        traitors_team1 = int(traitor_team1_spin.get())
    except ValueError:
        # handle invalid or empty value
        traitors_team1 = 0  # or set a default value or show an error to the user

    try:
        traitors_team2 = int(traitor_team2_spin.get())
    except ValueError:
        # handle invalid or empty value
        traitors_team2 = 0 

    # Check randomized and unique position selections
    randomized_position = bool(randomized_var.get())
    unique_position = bool(unique_var.get())

    # You can print the data or send/store it based on your application's needs
    print(f"Team 1 Players: {team1}")
    print(f"Team 2 Players: {team2}")
    print(f"Traitors in Team 1: {traitors_team1}")
    print(f"Traitors in Team 2: {traitors_team2}")
    print(f"Randomize Position: {randomized_position}")
    print(f"Unique Position: {unique_position}")

    roles1 = create_roles_list(len(team1), traitors_team1)
    roles2 = create_roles_list(len(team2), traitors_team2)

    if randomized_position:
        # for testing purpose
        # print('\nfinish sending roles without pos, now send rles with pos\n')
        send_roles_with_positions(team1, team2, roles1, roles2, positions, 5, False, 'not_exist', favored_weight=10, uniqueness=unique_position)
    else:
        # functions, comment the unused one when calling
        send_roles(team1, team2, roles1, roles2, False, 'not_exist', favored_weight=10)
    messagebox.showinfo("Info", "Roles sent successfully!")
    

def main_gui():
    root = tk.Tk()
    root.title("Team Selector")

    # Variables to store team selections
    team_selections = []

    # Display list of names with checkboxes
    for name in emails:
        if name != 'default':
            frame = ttk.Frame(root)
            frame.pack(pady=5, fill="x", padx=20)
            
            label = ttk.Label(frame, text=name, width=10)
            label.pack(side="left")
            
            team1_var = tk.IntVar()
            team2_var = tk.IntVar()
            
            team1_check = ttk.Checkbutton(frame, text="Team 1", variable=team1_var, 
                                        command=lambda v1=team1_var, v2=team2_var: v2.set(0))
            team1_check.pack(side="left", padx=10)
            
            team2_check = ttk.Checkbutton(frame, text="Team 2", variable=team2_var,
                                        command=lambda v1=team1_var, v2=team2_var: v1.set(0))
            team2_check.pack(side="left", padx=10)
            
            team_selections.append((name, team1_var, team2_var))

    # Number of traitors for both teams
    traitor_frame = ttk.Frame(root)
    traitor_frame.pack(pady=20, padx=20, fill="x")

    ttk.Label(traitor_frame, text="Traitors Team 1:").pack(side="left")
    traitor_team1_spin = ttk.Spinbox(traitor_frame, from_=0, to=5)
    traitor_team1_spin.pack(side="left", padx=10)

    ttk.Label(traitor_frame, text="Traitors Team 2:").pack(side="left")
    traitor_team2_spin = ttk.Spinbox(traitor_frame, from_=0, to=5)
    traitor_team2_spin.pack(side="left", padx=10)

    # Randomized and unique position checkboxes
    position_frame = ttk.Frame(root)
    position_frame.pack(pady=20, padx=20, fill="x")

    randomized_var = tk.IntVar()
    unique_var = tk.IntVar()

    randomized_check = ttk.Checkbutton(position_frame, text="Randomize Position", variable=randomized_var)
    randomized_check.pack(side="left", padx=10)
    unique_check = ttk.Checkbutton(position_frame, text="Unique Position", variable=unique_var)
    unique_check.pack(side="left", padx=10)

    # Send button
    send_button = ttk.Button(root, text="Send", command=lambda: send_teams(team_selections, traitor_team1_spin, traitor_team2_spin, randomized_var, unique_var))
    send_button.pack(pady=20)

    root.mainloop()


if __name__ == "__main__":
    # List of roles and email addresses, create two roles lists for more flexibility on num of players
    roles1 = ['traitor', 'good', 'good', 'good']
    roles2 = ['traitor', 'good', 'good', 'good'] 
    # add player's email
    emails = load_emails_from_file('emails.txt')

    # email credentials
    email_host = 'smtp.gmail.com'  # Email host
    email_port = 587  # Port for sending email
    email_address = 'chenjiaqi0218@gmail.com'
    email_password = 'lxun ceth djbz ioed'

    # Establishing a secure session with Gmail's outgoing SMTP server using TLS
    server = smtplib.SMTP(email_host, email_port)
    server.starttls()

    # Login to the email account
    server.login(email_address, email_password)
    
    # The default position list.  
    positions = ['top', 'mid', 'jg', 'ad', 'sup',
                'top', 'mid', 'jg', 'ad', 'sup',
                'top', 'mid', 'jg', 'ad', 'sup',
                'top', 'mid', 'jg', 'ad', 'sup',
                'top', 'mid', 'jg', 'ad', 'sup']
    
    main_gui()
    server.quit()
    # arbitrarily assign groups, the predetermined traitor's email must come at the first element.
    # group1, group2, num_traitors_group1, num_traitors_group2, random_positions, unique, predetermined, traitor_name, positions, num_positions = get_user_input()
    # traitor_email = emails[traitor_name]
    # pyinstaller --onefile GUI.py

