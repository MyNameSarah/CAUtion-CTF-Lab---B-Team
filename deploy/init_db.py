import sqlite3

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    c.execute('CREATE TABLE IF NOT EXISTS accounts (username TEXT, dummy_pw TEXT)')
    c.execute('DELETE FROM accounts')
    c.execute("INSERT INTO accounts VALUES ('guest', 'guest_key_1234')")
    c.execute("INSERT INTO accounts VALUES ('admin', 'admin_fake_key_9999')")
    
    c.execute('CREATE TABLE IF NOT EXISTS secret_vault_8f2a (top_secret TEXT, flag_val TEXT)')
    c.execute('DELETE FROM secret_vault_8f2a')
    c.execute("INSERT INTO secret_vault_8f2a VALUES ('TOP_SECRET', 'FLAG{m4st3r_0f_sq1_4nd_d3vt00ls}')")
    
    conn.commit()
    conn.close()
    print("[+] Hardcore DB Init Complete!")

if __name__ == '__main__':
    init_db()