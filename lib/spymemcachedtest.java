package com.techfundaes.memcacheBag;

import java.net.InetSocketAddress;
import java.util.Date;

import net.spy.memcached.MemcachedClient;

public class StoreObjectsInCache
{
    public static void main(String[] args) throws Exception
    {
        MemcachedClient memcacheClient = new MemcachedClient(new InetSocketAddress("localhost", 5555));

        Object objectToCache = new Object();
        memcacheClient.set("keyObject", 3600, objectToCache);

        Date startDate = new Date();
        memcacheClient.set("keyDate", 3600, startDate);
    }
}
