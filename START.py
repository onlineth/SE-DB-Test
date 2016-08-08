import functions
import test
import sys

# Starts with the UserID being 0 for anonymous
userID = 0

while 1:
    # Main Root menu
    choice = functions.menu(['User', 'Mode', 'Exit'], 'Root Menu')
    if choice == 'User':
        # User
        userID = functions.user()
    elif choice == 'Mode':
        # Mode
        while 1:
            choice = functions.menu(['Learn', 'Scan', 'Examine', 'Exit'], "Mode Menu", ['Root'])
            if (choice == 'Learn'):
                while 1:
                    choice = functions.menu(['Single Electron', 'Double Electron', 'Exit'], "Learn Menu", ['Root', 'Mode'])
                    if (choice == 'Single Electron'):
                        while 1:
                            functions.learn(0)
                            rin = raw_input('Another? 0 for no - Enter for Yes\n')
                            if rin != '':
                                if(int(rin) == 0):
                                    break
                    elif (choice == 'Double Electron'):
                        while 1:
                            functions.learn(1)
                            rin = raw_input('Another? 0 for no - Enter for Yes\n')
                            if rin != '':
                                if(int(rin) == 0):
                                    break
                    else:
                        break
            elif (choice == 'Scan'):
                # The actual test
                test.test(userID)
            elif (choice == 'Examine'):
                functions.examine()
            else:
                break
    else:
        # Exit
        print "Goodbye"
        sys.exit()
