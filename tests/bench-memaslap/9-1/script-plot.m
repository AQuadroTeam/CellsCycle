 plot(time, number_machines,'LineWidth',5)
 grid on
 title('Benchmark - 600 s dual memaslap load 9:1')
 ylabel('CellCycle instances')
 xlabel('sec (0-600 is memaslap time)')
 set(gca,'ZTick',[0:1:11])
 set(gca,'XTick',[0:60:1000])
 