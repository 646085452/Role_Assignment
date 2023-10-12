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

def save_emails_to_file(filename, emails):
    with open(filename, 'w') as file:
        for name, email in emails.items():
            file.write(f"{name},{email}\n")

def get_user_input():
    # Display the current list of names and emails
    print(Fore.YELLOW + "\nCurrent list of names:")
    for name, email in emails.items():
        if name != 'default':
            print(Fore.CYAN + f"{name}")
    
    # Ask the user if they want to add new people
    while True:
        choice = input(Fore.GREEN + "\nDo you want to add(a) or delete(d) a person from the list or neither(n)? (a/d/n): ").strip().lower()

        if choice == "a":
            name = input(Fore.YELLOW + "Enter the adding name: ").strip()
            email = input(Fore.YELLOW + "Enter the email: ").strip()
            emails[name] = email
            save_emails_to_file('emails.txt', emails)
            
        elif choice == "d":
            name = input(Fore.YELLOW + "Enter the deleting name: ").strip()
            if name in emails:
                del emails[name]
                save_emails_to_file('emails.txt', emails)
                print(Fore.GREEN + f"Name '{name}' deleted successfully!")
            else:
                print(Fore.RED + f"Name '{name}' not found!")
                
        elif choice == "n":
            break
        else:
            print(Fore.RED + "Invalid choice. Please answer with 'a', 'd', or 'n'.")
    
    # Ask for the number of people in group1 and group2
    while True:
        try:
            num_group1 = int(input(Fore.YELLOW + "\nEnter the number of people in Team 1: "))
            num_group2 = int(input(Fore.YELLOW + "Enter the number of people in Team 2: "))
            
            if num_group1 > 0 and num_group2 > 0:
                break  # Exit the loop if the input is valid
            else:
                print(Fore.RED + "Numbers must be greater than 0. Please try again.")
        except ValueError:  # Handle non-integer input
            print(Fore.RED + "Invalid input. Please enter a positive integer.")
    
    # Ask if the user wants the traitor to be manually set(predetermined)
    while True:
        predetermined_choice = input(Fore.GREEN + "\nDo you want to manually assign a player to be the traitor? (only one player for now) (y/n): ").strip().lower()
        if (yn_check(predetermined_choice)): break

    traitor_name = 'default'
    if predetermined_choice == 'y':
        predetermined = True 
        print(Fore.RED + "Your traitor name must be in the email group!! Nonexisted name will cause the program to terminate!!")
        
        # Get user input for the traitor name
        while True:
            traitor_name = input(Fore.YELLOW + "Your predetermined traitor name is: ").strip().upper()
            
            # Check if the input is not empty
            if traitor_name:
                break
            else:
                print(Fore.RED + "Invalid input. Name cannot be empty.")
        
        print(Fore.RED + "All set. Attention: The designated traitor must be the first person in the team to be assigned a traitor role with greater possibility.")
    else:
        predetermined = False

    # Ask for names of people in each group
    available_names = [name for name in emails if name != 'default']
    print(Fore.GREEN + "\nSelect names for Group 1:")
    group1 = select_names_from_list(num_group1, available_names)
    print(Fore.GREEN + "\nSelect names for Group 2:")
    group2 = select_names_from_list(num_group2, available_names)
    if (predetermined):
        if (group1[0] != emails[traitor_name] and group2[0] != emails[traitor_name]):
            print(Fore.RED + "The first player in either group does not match with your designated traitor name! Please restart.") 
            time.sleep(5)
            sys.exit()
    
    # Ask for the number of traitors in each group
    num_traitors_group1 = int(input(Fore.YELLOW + f"\nEnter the number of traitors in Team 1 (0 to {num_group1}): "))
    num_traitors_group2 = int(input(Fore.YELLOW + f"Enter the number of traitors in Team 2 (0 to {num_group2}): "))

    # Ask if the user wants random positions
    unique = False
    while True:
        random_positions_choice = input(Fore.GREEN + "\nDo you also want to assign positions? (y/n): ").strip().lower()
        if (yn_check(random_positions_choice)): break
    random_positions = True if random_positions_choice == 'y' else False
    # The default position list.  
    positions = ['top', 'mid', 'jg', 'ad', 'sup',
                'top', 'mid', 'jg', 'ad', 'sup',
                'top', 'mid', 'jg', 'ad', 'sup',
                'top', 'mid', 'jg', 'ad', 'sup',
                'top', 'mid', 'jg', 'ad', 'sup']
        
    num_default_positions = 5  # The default number of unique positions
    
    if random_positions:
        # Asking user to customize positions
        print(Fore.GREEN + "\nThe default positions are top, jg, mid, ad, sup.")
        while True:
            choice = input(Fore.GREEN + "Do you want to customize the positions? (y/n): ").strip().lower()
            if (yn_check(choice)): break

        # If user chooses to customize positions
        if choice == 'y':
            while True:
                try:
                    num_positions = int(input(Fore.GREEN + "\nHow many positions do you want to input? ").strip())
                    if num_positions > 0:
                        break
                    else:
                        print(Fore.RED + "Please input a positive integer.")
                except ValueError:
                    print(Fore.RED + "Invalid input. Please enter a number.")

            new_positions = []
            for i in range(num_positions):
                position = input(Fore.GREEN + f"Enter position {i+1}: ").strip()
                new_positions.append(position)

            positions = new_positions * 5
        else: 
            num_positions = num_default_positions
        
        # Ask if the user wants unique positions
        while True:
            unique_positions = input(Fore.GREEN + "\nDo you want positions to be unique? (y/n): ").strip().lower()
            if (yn_check(unique_positions)): break
        unique = True if unique_positions == 'y' else False


    return group1, group2, num_traitors_group1, num_traitors_group2, random_positions, unique, predetermined, traitor_name, positions, num_positions,

if __name__ == "__main__":
    # List of roles and email addresses, create two roles lists for more flexibility on num of players
    roles1 = ['traitor', 'good', 'good', 'good']
    roles2 = ['traitor', 'good', 'good', 'good'] 
    # add player's email
    emails = load_emails_from_file('emails.txt')
    
    # arbitrarily assign groups, the predetermined traitor's email must come at the first element.
    group1, group2, num_traitors_group1, num_traitors_group2, random_positions, unique, predetermined, traitor_name, positions, num_positions = get_user_input()
    traitor_email = emails[traitor_name]

    roles1 = create_roles_list(len(group1), num_traitors_group1)
    roles2 = create_roles_list(len(group2), num_traitors_group2)

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
    
    if random_positions:
        # for testing purpose
        # print('\nfinish sending roles without pos, now send rles with pos\n')
        send_roles_with_positions(group1, group2, roles1, roles2, positions, num_positions, predetermined, traitor_email, favored_weight=10, uniqueness=unique)
    else:
        # functions, comment the unused one when calling
        send_roles(group1, group2, roles1, roles2, predetermined, traitor_email, favored_weight=10)
    server.quit()
    # pyinstaller --onefile Role_Assignment.py

