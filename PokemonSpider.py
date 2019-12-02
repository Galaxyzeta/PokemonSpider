'''
Pokemon Info Spider
Author: @Galaxyzeta
Special Thanks to https://wiki.52poke.com
'''
import requests
from bs4 import BeautifulSoup
import re

def writePokemonDataToFile(code, fileName):
    # Search pokemon id and get its detailed url.
    url = "https://wiki.52poke.com/wiki/"+code
    headers = {
        "Connection": "keep-alive",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
    }
    html = ''
    sess = requests.Session()
    try:
        html = sess.get(url=url, headers=headers).content.decode('utf-8')
    except Exception as e:
        print(e.args)
        return False
    print("readOK")
    soup = BeautifulSoup(html,'html.parser')
    # Find pokemon name
    newhref = soup.select('.mw-parser-output b')[1].find(name='a').attrs['href']
    # Access pokemon info page and write html into a text file
    html = sess.get(url="https://wiki.52poke.com"+newhref, headers=headers).content.decode('utf-8')
    file = open(fileName+".txt", mode='w',encoding='utf-8')
    file.write(html)
    return True
    

def getPokemonDataByText(fileName, code):
    data = {}
    # Extract pokemon data
    soup = BeautifulSoup(readPokemonHtml(fileName+'.txt'), 'html.parser')
    mainsoup = soup.select('.a-r.at-c')[0]
    maintree = mainsoup.select('table.a-r.at-c>tbody>tr')
    # Step1: Get pokemon index and name: 
    data['PokeIndex'] = code
    tmplist = []
    # Format: 'Name':[CHS, JAP, ENG]
    tmpsoup = mainsoup.select('td.textblack')[0].select('b')
    for i in range(3):
        tmplist.append(tmpsoup[i].text)
    data['Name'] = tmplist
    # Step2: Get Attribute CHS Name to fit CSS.
    # Format: 'Type1': xx, 'Type2': xx
    '''
    attributeArray = soup.select('table.a-r.roundy')[0].attrs['class'][3:]
    data['Type1'] = attributeArray[0][3:]
    data['Type2'] = attributeArray[1][2:]
    '''
    data['Type1'] = {}
    data['Type2'] = {}
    # Step3: Get Special Ability Data
    tmpsoup = maintree[3].select('table.bgwhite td')
    tmplist = []
    tmplist2 = []
    for i in range(len(tmpsoup)):
        try:
            int(tmpsoup[i].text[0])
        except:
            _ = len(tmpsoup[i].select('a'))
            for j in range(_):
                if(len(tmpsoup[i].select('small'))==0):
                    tmplist.append(tmpsoup[i].select('a')[j].text)
                else:
                    tmplist2.append(tmpsoup[i].select('a')[0].text)
    data['Abilities-Normal'] = tmplist
    data['Abilities-Hide'] = tmplist2

    # Step4: Get Egg Data
    altindex = 11
    try:
        re.search(r'>(.*)<a',str(tmpsoup[1]),flags=re.M|re.S).group(1)
    except:
        altindex = 10
    tmpsoup = maintree[altindex].select('table.bgwhite td')
    tmplist = []
    tmp = tmpsoup[0].select('a')
    _ = len(tmp)
    for i in range(_):
        tmplist.append(tmp[i].text)
    data['EggTypes'] = tmplist
    del tmplist
    data['EggSteps'] = re.search(r'>(.*)<a',str(tmpsoup[1]),flags=re.M|re.S).group(1).rstrip()

    # Step5: Get Ability Data
    # Format: 'Ablility':{'Name':[Hp, Atk, Def, SpAtk, SpDef, Spd, Total], 'Name2':[... ...], ...}
    data['Stats'] = {}
    judge = 0
    target_id = '种族值'
    try:
        if soup.find('span', attrs={'id':target_id}).findNext('div').find('br', attrs={'style': 'clear:both'}) is not None:
            judge = 1
    except:
        target_id = '種族值'
    tmpsoup = soup.select('div.tabber')
    # judge = tmpsoup[0].findPrevious(name="h4").findNext().attrs['id'] == '种族值'
    form_name_list = ['一般']
    tmpsoup = []
    if judge == 0:
        tmpsoup.append(soup.find('span', attrs={'id':target_id}).findNext('table'))
        _ = tmpsoup[0]
        data['Type1'][form_name_list[0]] = _.attrs['class'][0][3:]
        data['Type2'][form_name_list[0]] = _.attrs['class'][1][3:]
    else:
        tmpsoup = soup.select('div.tabber')[0].select('div.tabbertab')
        form_name_list = []
        newli = []
        for i in range(len(tmpsoup)):
            if tmpsoup[i].find('br', attrs={'style':'clear:both'}) is not None:
                newli.append(tmpsoup[i])
                form_name_list.append(tmpsoup[i].attrs['title'])
                # Get different Types
                _ = tmpsoup[i].find('table')
                data['Type1'][form_name_list[i]] = _.attrs['class'][0][3:]
                data['Type2'][form_name_list[i]] = _.attrs['class'][1][3:]
        tmpsoup = newli
    '''
    if(len(tmpsoup) == 1):
        tmpsoup = []
        tmpsoup.append(soup)
    else:
        if judge == False:
            tmpsoup = []
            tmpsoup.append(soup.find('span', attrs={'id':'种族值'}).findNext('table'))
            print(tmpsoup)
        else:
            tmpsoup = soup.select('div.tabber')[0].select('div.tabbertab')
            form_name_list = [tmpsoup[i].attrs['title'] for i in range(len(tmpsoup))]
    '''
    ind = 0
    for s in tmpsoup:
        tmplist=[]
        tmplist.append(int(s.select('table th.bgl-HP')[1].text))
        tmplist.append(int(s.select('table th.bgl-攻击')[1].text))
        tmplist.append(int(s.select('table th.bgl-防御')[1].text))
        tmplist.append(int(s.select('table th.bgl-特攻')[1].text))
        tmplist.append(int(s.select('table th.bgl-特防')[1].text))
        tmplist.append(int(s.select('table th.bgl-速度')[1].text))
        tmplist.append(sum(tmplist[:6], 0))
        data['Stats'][form_name_list[ind]] = tmplist
        ind += 1
        del(tmplist)
    print(data)
    return data


def readPokemonHtml(file_name):
    file = open(file_name, mode='r',encoding='utf-8')
    res = file.read()
    file.close()
    return res

def parseCsv(data:dict):
    # Format:
    # Index, CHSName(WithFormInfomation), JAPName, ENGName, Type1, Type2, Ability1, Ability2, Ability3, EggType1, EggType2, EggStep, Hp, Atk, Def, SpAtk, SpDef, Spd, Total
    res = ""
    # Get Form Numbers
    for k, v in data['Stats'].items():
        tmplist = []
        tmplist.append(data['PokeIndex'])
        # Names
        for j in range(3):
            tmplist.append(data['Name'][j]+("" if k == '一般' or j != 0 else '-'+k))
        # Types
        tmplist.append(data['Type1'][k])
        if(data['Type1'][k] == data['Type2'][k]):
            tmplist.append("")
        else:
            tmplist.append(data['Type2'][k])
        # Abilities
        _ = len(data['Abilities-Normal'])
        for i in range(_):
            tmplist.append(data['Abilities-Normal'][i])
        if _ == 1:
            tmplist.append("")
        if len(data['Abilities-Hide']) == 1:
            tmplist.append(data['Abilities-Hide'][0])
        else:
            tmplist.append("")
        # EggTypes
        _ = len(data['EggTypes'])
        for i in range(_):
            tmplist.append(data['EggTypes'][i])
        if _ == 1:
            tmplist.append("")
        # EggSteps
        tmplist.append(data['EggSteps'])
        # Stats
        for i in range(7):
            tmplist.append(str(data['Stats'][k][i]))
        res += (','.join(tmplist))
        res += '\n'
        del tmplist
    return res
        

def numberToString(num:int):
    if num<10:
        return '00'+str(num)
    elif num<100:
        return '0'+str(num)
    else:
        return str(num)

def startSpider(start:int, end:int, target, mode='a+'):
    # headers = "Index,CHSName,JAPName,ENGName,Type1,Type2,Ability1,Ability2,Ability3,EggType1,EggType2,EggStep,Hp,Atk,Def,SpAtk,SpDef,Spd,Total\n"
    # file.write(headers)
    for i in range(start, end+1):
        file = open(target, mode=mode, encoding="utf-8")
        timeout = 5
        string = numberToString(i)
        print(string)
        while timeout>0:
            if writePokemonDataToFile(code=string, fileName=FILENAME) == True:
                break
            else:
                timeout -= 1
        else:
            print('Connection Error, System Exit!')
            exit(-1)
        _ = getPokemonDataByText(code=string, fileName=FILENAME)
        _ = parseCsv(_)
        print(_)
        file.write(_)
        file.close()

if __name__ == "__main__":
    #writePokemonDataToFile('567')
    FILENAME = "test"
    startSpider(350, 890, "lib.csv", mode='a+')
