import memcache
mc = memcache.Client(['localhost:5555'], debug=1)

print "here i set some_key : Some value"
print mc.set("some_key", "Some value")
print "here i get some_key"
print mc.get("some_key")

print "here i set another_key : 3"
print mc.set("another_key", 3)
print "here i get another_key"
print mc.get("another_key")
print "here i set another_key : 55"
print mc.set("another_key", 55)
print "here i get another_key"
print mc.get("another_key")
