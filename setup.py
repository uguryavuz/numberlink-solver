from pip._internal import main

for library in ['ortools', 'pygame', 'pygbutton']:
    main(['install', library])
