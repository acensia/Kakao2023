import time
import requests as rq
import json

x_auth_token = 'a3174d3442b17a8900569bc38f619a25'
base_url = 'https://68ecj67379.execute-api.ap-northeast-2.amazonaws.com/api'
Content_type = 'application/json'

W_ = [20, 200]
H_ = [3, 10]
Full_date_ = [200, 1000]
Rsv_ = [1, 4]
Chk_ = [20, 100]
Rate_ = [60, 75]

REFUSED = "refused"
ACCEPTED = "accepted"
DELAYED = "delayed"

class room:
    def __init__(self):
        self.cal = []
        
    def reservation(self, a, b):
        self.cal.append([a, b-1])
        
    def empty(self, a, b):
        for r in self.cal:
            if not (b <= r[0] or a > r[1]):
                return False
        return True
# start ############################################
def start(pid):
    header = {
        'X-Auth-Token' : x_auth_token,
        'Content-Type' : Content_type
    }
    data = {
        "problem" : pid
    }
    start = base_url + '/start'
    res = rq.post(start, headers= header, json= data)
    res_js = res.json() if res and res.status_code == 200 else None
    return res_js

#########################################
def acceptable(n, rooms, H, W):
    chkin = n["check_in_date"]
    chkout = n["check_out_date"]
    am = n["amount"]
    id = n["id"]
    head = 0
    for h in range(H):
        cnt = 0
        tail = 0
        for w in range(W):
            if rooms[h][w].empty(chkin, chkout):
                cnt += 1
            else :
                cnt = 0
            if cnt == am:
                tail = w
                break
        if cnt == am:
            head = (h+1)*1000 + tail + 2 - am
            break
    return head != 0

# new requests ######################
def new_rq(header):
    nrq = base_url + '/new_requests'
    res = rq.get(nrq, headers= header)
    res_js = res.json() if res and res.status_code == 200 else None
    # print("new rq", res_js)
    return res_js['reservations_info']

##########################################3
def reply_chk(n, rooms, H, W, today):
    chkin = n["check_in_date"]
    if chkin - 1 == today or today == n["request"] + 14 :
        res = findRoom(n, rooms, H, W)
        if res != 0:
            n["headroom"] = res
            return ACCEPTED
        return REFUSED
    return DELAYED

## reply #############################################
def reply(header, list):
    rep = base_url + '/reply'
    data = {
        "replies" : list
    }
    res = rq.put(rep, headers= header, json= data)
    res_js = res.json() if res and res.status_code == 200 else None
    # print("rep", res_js)
    
###########################################
def findRoom(n, rooms, H, W):
    chkin = n["check_in_date"]
    chkout = n["check_out_date"]
    am = n["amount"]
    id = n["id"]
    head = 0
    h_ = 0
    w_ = 0
    for h in range(H):
        cnt = 0
        tail = 0
        for w in range(W):
            if rooms[h][w].empty(chkin, chkout):
                cnt += 1
            else :
                cnt = 0
            if cnt == am:
                tail = w
                break
        if cnt == am:
            h_ = h
            w_ = tail + 1 - am
            head = (h+1)*1000 + tail + 2 - am
            break
    if head != 0:
        for m in range(am):
            rooms[h_][w_+m].reservation(chkin, chkout)
    return head

# simulate #######################################33
def simul(header, ass, ref_cnt, acc_cnt, rq_cnt):
    sim = base_url + '/simulate'
    data = {
        "room_assign" : ass
    }
    
    
    res = rq.put(sim, headers= header, json= data)
    res_js = res.json() if res and res.status_code == 200 else None
    print(rq_cnt, ", ", acc_cnt, ", ", ref_cnt, "/ simul", res_js)
    #print("Today :", res_js["day"] - 1)
    
    
# score #####################3
def score(header):
    scr = base_url + '/score'
    
    res = rq.get(scr, headers= header)
    res_js = res.json() if res and res.status_code == 200 else None
    print("score", res_js)
    
############################################################

def main(pid):
    pid = pid - 1
    W = W_[pid]
    H = H_[pid]
    FD = Full_date_[pid]
    Resv = Rsv_[pid]
    ChkD = Chk_[pid]
    Rate = Rate_[pid]
    
    hotel = [[0 for i in range(W)] for i in range(H)]
    
    start_js = start(pid+1)
    auth_key = start_js['auth_key']
    header = {
        'Authorization' : auth_key,
        'Content-Type' : Content_type
    }
    hotel_cal = [[[0 for i in range(W)] for i in range(H)] for i in range(FD)]
    rooms = [[room() for i in range(W)] for i in range(H)]
    accepted = []
    
    acceptable_rsv = []
    ref_cnt = 0
    acc_cnt = 0
    rq_cnt = 0
    for i in range(1, FD + 1):
        nlist = new_rq(header)
        #print("RQ : \n", nlist)
        rlist = []
        #'''
        for n in nlist:
            rq_cnt += 1
            if acceptable(n, rooms, H, W):
                n["request"] = i
                acceptable_rsv.append(n)
            else :
                ans = {"id" : n["id"], "reply" : REFUSED}
                rlist.append(ans)
        '''
        for n in nlist:
            chkin = n["check_in_date"]
            chkout = n["check_out_date"]
            am = n["amount"]
            id = n["id"]
            rep = "refused"
            head = 0
            for h in range(H):
                cnt = 0
                tail = 0
                for w in range(W):
                    if rooms[h][w].empty(chkin, chkout):
                        cnt += 1
                    else :
                        cnt = 0
                    if cnt == am:
                        tail = w
                        break
                if cnt == am:
                    rep = "accepted"
                    for w in range(am):
                        rooms[h][tail - w].reservation(chkin, chkout)
                    head = (h+1)*1000 + tail + 2 - am
                    break
                    
            ans = { "id" : id, "reply" : rep}
            ref_cnt += 1
            if rep == "accepted":
                ref_cnt -= 1
                acc_cnt += 1
                rsv = {"id":id, "headroom" : head, "amount" : am, "in" : chkin, "out" : chkout}
                rlist.append(ans)
                accepted.append(rsv)
        '''
        #print("possi : \n", acceptable_rsv)
        for n in acceptable_rsv[:]:
            rq_chk = reply_chk(n, rooms, H, W, i)
            if not rq_chk == DELAYED :
                rep = rq_chk
                ans = {"id" : n["id"], "reply" : rep}
                ref_cnt += 1
                if rep == ACCEPTED :
                    ref_cnt -= 1
                    acc_cnt += 1
                    rsv = {"id":n["id"], "headroom" : n["headroom"], "in" : n["check_in_date"], "out" : n["check_out_date"]}
                    accepted.append(rsv)
                rlist.append(ans)
                acceptable_rsv.remove(n)
                #print("after : \n", acceptable_rsv)
        #'''
        asslist = []
        for acc in accepted[:]:
            if i == acc["in"]:
                ass = {"id" : acc["id"], "room_number" : acc["headroom"]}
                asslist.append(ass)
                accepted.remove(acc)
        reply(header, rlist)
        #print("rli : ", rlist)
        #print("assli : ", asslist)
        simul(header, asslist, ref_cnt, acc_cnt, rq_cnt)
    score(header)

print("prob 1")    
main(1)
time.sleep(3)
print("prob 2")
main(2)