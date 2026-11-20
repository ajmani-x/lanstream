# NS-2 UDP/CBR model of media transport (not the JPEG application itself).
# ns experiments/streaming.tcl 10ms 0.02 2Mb baseline
# Arguments: bottleneck delay, random loss probability, offered rate, output prefix
set delay [lindex $argv 0]
if {$delay == ""} {set delay 10ms}
set loss [lindex $argv 1]
if {$loss == ""} {set loss 0.0}
set rate [lindex $argv 2]
if {$rate == ""} {set rate 2Mb}
set prefix [lindex $argv 3]
if {$prefix == ""} {set prefix simulation}
set ns [new Simulator]
set trace [open "$prefix.tr" w]
$ns trace-all $trace
set n0 [$ns node]
set n1 [$ns node]
set n2 [$ns node]
$ns duplex-link $n0 $n1 10Mb 1ms DropTail
$ns duplex-link $n1 $n2 3Mb $delay DropTail
$ns queue-limit $n1 $n2 40
set error [new ErrorModel]
$error unit pkt
$error set rate_ $loss
$error ranvar [new RandomVariable/Uniform]
$error drop-target [new Agent/Null]
$ns lossmodel $error $n1 $n2
set udp [new Agent/UDP]
$ns attach-agent $n0 $udp
set sink [new Agent/LossMonitor]
$ns attach-agent $n2 $sink
$ns connect $udp $sink
set cbr [new Application/Traffic/CBR]
$cbr set packetSize_ 1192
$cbr set rate_ $rate
$cbr set random_ false
$cbr attach-agent $udp
proc finish {} {
    global ns trace sink
    $ns flush-trace
    puts "Received packets: [$sink set npkts_]"
    puts "Received bytes: [$sink set bytes_]"
    close $trace
    exit 0
}
$ns at 1.0 "$cbr start"
$ns at 11.0 "$cbr stop"
$ns at 12.0 "finish"
$ns run
