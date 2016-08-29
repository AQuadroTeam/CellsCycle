figure(1)
plot(get_lla_nu, 'Color', 'green')
hold on
plot(get_lla_u)
hold on
plot(get_lld, 'Color', 'yellow')
hold on
legend('get-lla-nu','get-lla-u','get-lld')
title('Comparison between lla with Push LIFO and FIFO and lld')
ylabel('sec (lower is better)')

%%
figure(4)
plot(set_lla_nu, 'Color', 'green')
hold on
plot(set_lla_u)
hold on
plot(set_lld, 'Color', 'yellow')
legend('set-lla-nu', 'set-lla-u', 'set-lld')
title('Comparison between lla with Push LIFO and FIFO and lld')
ylabel('sec (lower is better)')

%%

figure(2)
plot(get_st_a, 'Color', 'green')
hold on
plot(get_st_lla)
hold on
plot(set_st_a, 'Color', 'green')
hold on
plot(set_st_lla)
legend('get-st-a','get-st-lla', 'set-st-a', 'set-st-lla')
title('Comparison between SplayTree+Array vs SplayTree+LLA')
ylabel('sec (lower is better)')

%%

figure(3)
plot(get_lla_u, 'Color', 'green')
hold on
plot(get_st_lla)
hold on
plot(set_lla_u, 'Color', 'green')
hold on
plot(set_st_lla)
legend('get-lla-u','get-st-lla', 'set-lla-u', 'set-st-lla')
title('Comparison between best SplayTree and best LinkedList lla-u')
ylabel('sec (lower is better)')





%%
colors = [255 255 0; 0 255 0; 255 102 0];


figure(1)
a = [get_lla_nu, get_lla_u  ,  get_lld];
bar_handle = bar(a,'grouped');
set(bar_handle(1),'FaceColor',[1, 1, 0])
set(bar_handle(2),'FaceColor',[0 ,1, 0])
set(bar_handle(3),'FaceColor',[1, 0.23, 0])
set(gca,'XTick',[1:1:23])
legend('get-lla-nu','get-lla-u','get-lld')
grid on
title('Comparison of "get" between lla with Push LIFO and FIFO and lld')
ylabel('sec (lower is better)')

figure(2)
a = [set_lla_nu, set_lla_u  ,  set_lld]
bar_handle = bar(a,'grouped');
set(bar_handle(1),'FaceColor',[1, 1, 0])
set(bar_handle(2),'FaceColor',[0 ,1, 0])
set(bar_handle(3),'FaceColor',[1, 0.23, 0])
set(gca,'XTick',[1:1:23])
legend('set-lla-nu','set-lla-u','set-lld')
grid on
title('Comparison of "set" between lla with Push LIFO and FIFO and lld')
ylabel('sec (lower is better)')

figure(3)
a = [get_st_a, get_st_lla]
bar_handle = bar(a,'grouped');
set(bar_handle(1),'FaceColor',[1, 1, 0])
set(bar_handle(2),'FaceColor',[0 ,1, 0])
set(gca,'XTick',[1:1:23])
legend('get-st-a','get-st-lla')
grid on
title('Comparison "get" between SplayTree+Array vs SplayTree+LLA')
ylabel('sec (lower is better)')

figure(4)
a = [set_st_a, set_st_lla]
bar_handle = bar(a,'grouped');
set(bar_handle(1),'FaceColor',[1, 1, 0])
set(bar_handle(2),'FaceColor',[0 ,1, 0])
set(gca,'XTick',[1:1:23])
grid on
legend('set-st-a','set-st-lla')
title('Comparison "set" between SplayTree+Array vs SplayTree+LLA')
ylabel('sec (lower is better)')

figure(5)
a = [get_lla_u , get_st_lla]
bar_handle = bar(a,'grouped');
set(bar_handle(1),'FaceColor',[1, 1, 0])
set(bar_handle(2),'FaceColor',[0 ,1, 0])
set(gca,'XTick',[1:1:23])
grid on
legend('get-lla-u','get-st-lla')
title('Comparison "get" between best SplayTree and best LinkedList lla-u')
ylabel('sec (lower is better)')

figure(6)
a = [set_lla_u , set_st_lla]
bar_handle = bar(a,'grouped');
set(bar_handle(1),'FaceColor',[1, 1, 0])
set(bar_handle(2),'FaceColor',[0 ,1, 0])
set(gca,'XTick',[1:1:23])
grid on
legend('set-lla-u','set-st-lla')
title('Comparison "set" between best SplayTree and best LinkedList lla-u')
ylabel('sec (lower is better)')