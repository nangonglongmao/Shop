from django.shortcuts import render, redirect

from axf.models import SlideShow, MainDescription, Product, CategorieGroup, ChildGroup, User, Address, Cart, Order
import random
from axf.sms import send_sms
from django.http import JsonResponse
import uuid


# Create your views here.
def home(request):
    # 获取轮播图数据
    slideList = SlideShow.objects.all()
    # 获取5大模块数据
    mainList = MainDescription.objects.all()
    for item in mainList:
        products = Product.objects.filter(categoryId=item.categoryId)
        item.product1 = products.get(productId=item.product1)
        item.product2 = products.get(productId=item.product2)
        item.product3 = products.get(productId=item.product3)
    return render(request, "home/home.html", {"slideList": slideList, "mainList": mainList})


def market(request, gid, cid, sid):
    # 左侧分组数据
    leftCategorieList = CategorieGroup.objects.all()

    # 获取分组商品的信息
    products = Product.objects.filter(categoryId=gid)
    # 获取子类数据
    if cid != "0":
        products = products.filter(childId=cid)
    # 排序
    if sid == "1":
        # products = products.order_by()
        pass
    elif sid == "2":
        products = products.order_by("price")
    elif sid == "3":
        products = products.order_by("-price")

    # 获取子组信息
    childs = ChildGroup.objects.filter(categorie__categorieId=gid)

    return render(request, "market/market.html",
                  {"leftCategorieList": leftCategorieList, "products": products, "childs": childs, "gid": gid,
                   "cid": cid})


def cart(request):
    # 判断是否登录
    tokenValue = request.COOKIES.get("token")
    if not tokenValue:
        # 说明没有登录
        return redirect("/login/")
    try:
        user = User.objects.get(tokenValue=tokenValue)
    except User.DoesNotExist as e:
        return JsonResponse({"error": 2})
    carts = Cart.objects.filter(user__tokenValue=tokenValue)
    cartsAddress = Address.objects.filter(user = user)
    return render(request, "cart/cart.html", {"carts": carts,"cartsAddress":cartsAddress})


def qOrder(request):
    tokenValue = request.COOKIES.get("token")

    #找到当前可用的订单
    order = Order.orders2.filter(user__tokenValue=tokenValue).get(flag=0)
    order.flag = 1
    order.save()

    #属于该订单的购物选中数据的isOrder置位False
    carts = Cart.objects.filter(user__tokenValue=tokenValue).filter(order=order).filter(isCheck=True)
    for cart in carts:
        cart.isOrder = False
        cart.save()

    #讲没有被选中的数据添加到新的订单中
    newOrder =  Order.create(str(uuid.uuid4()), User.objects.get(tokenValue=tokenValue), Address.objects.get(pk=1), 0)
    newOrder.save()
    oldCarts = Cart.objects.filter(user__tokenValue=tokenValue)
    for cart in oldCarts:
        cart.order = newOrder
        cart.save()

    return JsonResponse({"error":0})




def changecart2(request):
    cartid = request.POST.get("cartid")
    cart = Cart.objects.get(pk=cartid)
    cart .isCheck = not cart.isCheck
    cart.save()
    return JsonResponse({"error":0, "flag":cart.isCheck})


def changecart(request, flag):
    num = 1
    if flag == "1":
        num = -1

    # 判断是否登录
    tokenValue = request.COOKIES.get("token")
    if not tokenValue:
        # 说明没有登录
        # return redirect("/login/")
        return JsonResponse({"error": 1})
    try:
        user = User.objects.get(tokenValue=tokenValue)
    except User.DoesNotExist as e:
        return JsonResponse({"error": 2})
        # return redirect("/login/")

    gid = request.POST.get("gid")
    cid = request.POST.get("cid")
    pid = request.POST.get("pid")
    product = Product.objects.filter(categoryId=gid, childId=cid).get(productId=pid)
    try:
        cart = Cart.objects.filter(user__tokenValue=tokenValue).filter(product__categoryId=gid).filter(
            product__childId=cid).get(product__productId=pid)
        if flag == "2":
            if product.storeNums == "0":
                return JsonResponse({"error": 0, "num": cart.num})

        # 已买过该商品，得到了该购物车的数据
        cart.num = cart.num + num
        product.storeNums = str(int(product.storeNums) - num)
        product.save()
        if cart.num == 0:
            cart.delete()
        else:
            cart.save()

    except Cart.DoesNotExist as e:
        if flag == "1":
            return JsonResponse({"error": 0, "num": 0})
        # 找一个可用的订单 isDelete为False,flag为0，在当期用户中的所有订单最多只能有一个订单为0
        try:
            order = Order.orders2.filter(user__tokenValue=tokenValue).get(flag=0)
        except Order.DoesNotExist as e:
            # 没有可用订单
            orderId = str(uuid.uuid4())
            address = Address.objects.get(pk=1)
            order = Order.create(orderId, user, address, 0)
            order.save()

        # 没有购买过该商品，需要创建该条购物车数据
        cart = Cart.create(user, product, order, 1)
        cart.save()
        product.storeNums = str(int(product.storeNums) - num)
        product.save()

    # 告诉客户端添加成功
    return JsonResponse({"error": 0, "num": cart.num})


def mine(request):
    phone = request.session.get("phoneNum", default="未登录")
    return render(request, "mine/mine.html", {"phone": phone})


from django.contrib.auth import logout


def quit(request):
    logout(request)
    return redirect("/mine/")


def login(request):
    tokenValue = request.COOKIES.get("token")
    if tokenValue:
        return redirect("/mine/")
    else:
        if request.method == "GET":
            if request.is_ajax():
                # 生产验证码
                strNum = '1234567890'
                # 随机选取4个值作为验证码
                rand_str = ''
                for i in range(0, 6):
                    rand_str += strNum[random.randrange(0, len(strNum))]
                msg = "您的验证码是：%s。请不要把验证码泄露给其他人。" % rand_str
                phone = request.GET.get("phoneNum")
                # send_sms(msg, phone)
                # 存入session
                request.session["code"] = rand_str
                print("**************", rand_str,"***************")
                response = JsonResponse({"data": "ok"})

                return response
            else:
                return render(request, "mine/login.html")
        else:
            phone = request.POST.get("username")
            passwd = request.POST.get("passwd")
            code = request.session.get("code")

            if passwd == code:
                # 验证码验证成功
                # 判断用户是否存在
                uuidStr = str(uuid.uuid4())
                try:
                    user = User.objects.get(pk=phone)
                    user.tokenValue = uuidStr
                    user.save()
                except User.DoesNotExist as e:
                    # 注册
                    user = User.create(phone, None, uuidStr, "sunck good")
                    user.save()
                request.session["phoneNum"] = phone
                response = redirect("/mine/")
                # 将tokenValue写入cookie
                response.set_cookie("token", uuidStr)
                return response
            else:
                # 验证码验证失败
                return redirect("/login/")


def showAddress(request):
    # 获取地址信息
    addresses = Address.objects.filter(user__phoneNum=request.session.get("phoneNum"))
    return render(request, 'mine/showAddress.html', {"addresses": addresses})


def addAddress(request):
    tokenValue = request.COOKIES.get("token")
    if not tokenValue:
        return redirect("/login/")
    else:
        if request.method == "GET":
            return render(request, "mine/addAddress.html")
        else:
            name = request.POST.get("name")
            sex = request.POST.get("sex")
            if sex == "0":
                sex = False
            else:
                sex = True
            telephone = request.POST.get("telephone")
            province = request.POST.get("province")
            city = request.POST.get("city")
            county = request.POST.get("county")
            street = request.POST.get("street")
            detail = request.POST.get("detail")
            postCode = request.POST.get("postCode")
            allAddress = province + city + county + street + detail + postCode
            phone = request.session.get("phoneNum")
            user = User.objects.get(pk=phone)
            address = Address.create(name, sex, telephone, postCode, allAddress, province, city, county, street, detail,
                                     user)
            address.save()
            return redirect("/addAddress/")


def showOrder(request):
    # 判断是否登录
    tokenValue = request.COOKIES.get("token")
    if not tokenValue:
        # 说明没有登录
        return redirect("/login/")
    try:
        user = User.objects.get(tokenValue=tokenValue)
    except User.DoesNotExist as e:
        return redirect("/login/")
    else:
        #获取订单信息
        # orders= Order.orders2.filter(user__tokenValue=tokenValue)
        return render(request, 'mine/showOrder.html')


def search(request):
    return render(request, 'base/search.html')


def evaluate(request):
    return render(request, 'mine/evaluate.html')


def ICQ(request):
    return render(request, 'mine/ICQ.html')


def about(request):
    return render(request, 'mine/about.html')