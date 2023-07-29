import ldap
import argparse
import getpass

# Disable certificate verification
ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
ldap.set_option(ldap.OPT_X_TLS_NEWCTX,0)
ldap.set_option(ldap.OPT_REFERRALS,0)

def get_base_dn(server_url, username="", password=""):
    conn = ldap.initialize(server_url)
    conn.simple_bind_s(username, password)

    # Perform a search to retrieve the base DN
    result = conn.search_s('', ldap.SCOPE_BASE, 'objectClass=*', ['namingContexts'])
    #print(result)
    base_dn = result[0][1]['namingContexts'][0].decode()

    conn.unbind()
    return base_dn


def get_user_list(server_url, base_dn, username=None, password=None, scope=ldap.SCOPE_SUBTREE, attributes=['cn']):
    conn = ldap.initialize(server_url)

    if username and password:
        conn.simple_bind_s(username, password)
    else:
        conn.simple_bind_s()

    # Perform a search to retrieve the user list
    result = conn.search_s(base_dn, scope, '(objectClass=user)', attributes)
    #print(result[0])
    #user_list = [entry[1]['cn'][0].decode('utf-8') for entry in result]
    user_list = [entry for dn, entry in result if isinstance(entry, dict)]
    conn.unbind()
    return user_list
    
def get_ou_list(server_url, base_dn, username=None, password=None, scope=ldap.SCOPE_SUBTREE):
    conn = ldap.initialize(server_url)

    if username and password:
        conn.simple_bind_s(username, password)
    else:
        conn.simple_bind_s()

    # Perform a search to retrieve the OU list
    result = conn.search_s(base_dn, scope, '(objectClass=organizationalUnit)', ['*'])
    #print(result[0])
    ou_list = [entry[0] for entry in result]
    conn.unbind()
    return ou_list


def get_user_attributes(server_url, base_dn, user_filter=None, username=None, password=None, attributes=['*']):
    conn = ldap.initialize(server_url)

    if username and password:
        conn.simple_bind_s(username, password)
    else:
        conn.simple_bind_s()

    # Perform a search to retrieve the user attributes
    #result = conn.search_s(base_dn, ldap.SCOPE_SUBTREE, user_filter, ['*'])
# Search for the user and retrieve all attributes
    try:
        search_filter = f"(|(cn={user_filter})(uid={user_filter}))"
        #attributes = ["*"]  # Retrieve all attributes
        result = conn.search_s(base_dn, ldap.SCOPE_SUBTREE, search_filter, attributes)
        #print(result)
        entries = result[0][1]
        #print(entries)
        return entries
    except ldap.LDAPError as e:
        print(f"LDAP search error: {e}")
        return []

    conn.unbind()
    #return user_attributes


def display_user_list(user_list, attributes=['cn']):
    #print(user_list)
    print('Users:\n-------------------------------')
    count = 0
    #print(attributes)
    for user in user_list:
        #cn = user.get('cn', [None])[0]
        for attr in attributes:
            attr_print = user.get(attr, [None])[0]
            if attr == attributes[0] and attr_print:
                print(attr_print.decode('utf-8'), end='')
            elif attr == attributes[0]: 
                None
            elif attr != attributes[0] and attr_print:
                print(",", end='')
                print(attr_print.decode('utf-8'), end='')
            else:
                print(",", end='')
        print("")
        count += 1
    print('Total Users: %s' % count)
    
def display_ou_list(ou_list):
    print('Organizational Units:')
    count = 0
    for ou in ou_list:
        if ou:
            print(ou)
            count += 1
    print('Total OUs: %s' % count)

def save_user_list_to_file(user_list, filename, attributes='cn'):
    with open(filename, 'w') as f:
        #f.write('Users:\n')
        count = 0
        for user in user_list:
            for attr in attributes:
                attr_print = user.get(attr, [None])[0]
                if attr == attributes[0] and attr_print: 
                        f.write(attr_print.decode('utf-8'))
                elif attr == attributes[0]:
                    None
                elif attr != attributes[0] and attr_print:
                    f.write(",")
                    f.write(attr_print.decode('utf-8'))
                else:
                    f.write(",")
            f.write("\n")
            count += 1
            #cn = user.get('cn', [None])[0]
            #if cn:
            #    cn=cn.decode('utf-8')
            #    f.write(cn + '\n')
            #    count += 1
    print('User list saved to', filename)
    print('Total Users: %s' % count)
    
def decode_or_print(value):
    if isinstance(value, bytes):  # Check if the variable is of type 'bytes'
        try:
            string_value = value.decode()  # Decode the byte variable to string
            #print(string_value)
            return string_value
        except UnicodeDecodeError:
            return value
    else:
        #print(value)
        return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Python LDAP Script')
    parser.add_argument('--server', required=True, help='LDAP server URL')
    parser.add_argument('--username', default='', help='LDAP username (optional)')
    parser.add_argument('--password', help='LDAP password (optional)')
    parser.add_argument('--basedn', help='Override the base DN (optional)')
    parser.add_argument('--search', help='Search for a specific user (optional)')
    parser.add_argument('--searchattr', help='List specific attributes, comma separated (optional like "cn,mail")')
    parser.add_argument('--listbasedn', default=False, action="store_true", help='List Organizational Units for BaseDN (optional)')
    parser.add_argument('--listallou', default=False, action="store_true", help='List Organizational Units for BaseDN (optional)')
    parser.add_argument('--output', help='Output to a file (optional)')

    args = parser.parse_args()
    
    if args.username and not args.password:
        args.password = getpass.getpass("Enter the password: ")
    if args.searchattr:
        args.searchattr = args.searchattr.split(",")

    base_dn = ""
    if args.basedn:
        base_dn = args.basedn
    else:
        base_dn = get_base_dn(args.server, args.username, args.password)
    print("Base DN: %s" % base_dn)
    
    if args.search:
        user_attributes = ""
        if args.searchattr:
            user_attributes = get_user_attributes(args.server, base_dn, args.search, args.username, args.password, args.searchattr)
        else:
            user_attributes = get_user_attributes(args.server, base_dn, args.search, args.username, args.password)
        if user_attributes:
            print('\nUser Attributes:')
            for attr_name, attr_value in user_attributes.items():
                print(f'{attr_name}: {decode_or_print(attr_value[0])}')
    elif args.listallou:
        ou = ""
        ou = get_ou_list(args.server, base_dn, args.username, args.password)
        if ou:
            display_ou_list(ou)
    elif args.listbasedn:
        ou = ""
        ou = get_ou_list(args.server, base_dn, args.username, args.password)
        if ou:
            display_ou_list(ou)
    else:
        user_list = ""
        if args.searchattr:
            user_list = get_user_list(args.server, base_dn, args.username, args.password, attributes=args.searchattr)
        else:
            user_list = get_user_list(args.server, base_dn, args.username, args.password)
        if args.output:
            if args.searchattr:
                save_user_list_to_file(user_list, args.output, args.searchattr)
            else:
                save_user_list_to_file(user_list, args.output)
        else:
            if args.searchattr:
                display_user_list(user_list, args.searchattr)
            else:
                display_user_list(user_list)
            print("done")
