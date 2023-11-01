import sqlite3 as sql
import xml.etree.ElementTree as ET

conn=sql.connect('my_libr.sqlite')
cur=conn.cursor()

cur.executescript('''

DROP TABLE IF EXISTS Artists;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artists( id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, Name TEXT NOT NULL UNIQUE );
CREATE TABLE Album( id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, Artist_id INTEGER NOT NULL, Album_Title TEXT NOT NULL UNIQUE );
CREATE TABLE Track( id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE, Album_id INTEGER NOT NULL, Title TEXT NOT NULL UNIQUE, Min INTEGER, Url VARCHAR UNIQUE );

''')

fname=input('*** ENTER SPOTIFY ACCOUNT FILE *** ')
if len(fname)==0:fname='liked.xml'

fhandle= ET.parse(fname)
info=fhandle.findall('Sheet1')
root=fhandle.getroot()

def lookup(dict,tag):
    found=False
    for child in dict:
        if child.tag==tag:
            found=True
        if found: return child.text
    return 'NA'
count=0
for i in info:
    song=lookup(i,'Track_x0020_Name')
    artist=lookup(i,'Artist_x0020_Name_x0028_s_x0029_')
    album=lookup(i,'Album_x0020_Name')
    url=lookup(i,'Track_x0020_Preview_x0020_URL')
    duration=lookup(i,'Track_x0020_Duration_x0020__x0028_ms_x0029_')
    count=count+1
    if song is None or artist is None or duration is None or album is None:continue

    print(artist,song,album,url,round((int(duration)/(60*10**3)),2),'min')

    cur.execute('INSERT or IGNORE into Artists (Name) VALUES(?)',(artist,))
    cur.execute('SELECT id FROM Artists WHERE Name=?',(artist,))
    artist_id=cur.fetchone()[0]

    cur.execute('INSERT or IGNORE into Album (Album_Title,Artist_id) VALUES(?,?)',(album,artist_id))
    cur.execute('SELECT id FROM Album WHERE Album_Title=?',(album,))
    album_id=cur.fetchone()[0]

    cur.execute('INSERT OR REPLACE into Track(Title,Album_id,Min,Url) VALUES (?,?,?,?)',
                (song,album_id,round(int(duration)/(60*10**3),2),url))
conn.commit()

print(count)

### useful but useless here codes
