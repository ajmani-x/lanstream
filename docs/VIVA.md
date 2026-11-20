# Viva and presentation notes

**What problem does this solve?** A peer shares video with several machines on a LAN without sending the media to an external service. The project exposes the effect of delay variation and loss on real-time playback.

**Why TCP and UDP together?** Session commands need ordered reliable delivery. Media prioritizes timeliness; a lost JPEG frame is skipped while later independent frames continue. TCP could carry media too, but retransmission and ordered delivery can delay later data.

**Is UDP always faster?** No. It avoids TCP reliability and ordering but has no automatic congestion control or guaranteed delivery. Performance depends on network conditions and application design.

**Why is this peer-to-peer?** Any instance can originate or receive streams. There is no dedicated central server. Within a stream the source peer acts as a server to its receiving peers. This version has no multi-hop peer relaying.

**Why JPEG?** Each frame is independently decodable and easy to split/reassemble, which makes loss experiments clear. The tradeoff is higher bandwidth than H.264 or H.265.

**Why not put an entire frame in one datagram?** Large packets can exceed UDP limits or require IP fragmentation. Small application chunks stay under a typical LAN MTU and identify exactly which portions of a frame arrived.

**What happens when a chunk is lost?** The frame is held until its deadline. If incomplete it is discarded. Subsequent JPEG frames can play without retransmitting the missing one.

**How do you reorder data?** Each chunk has a frame number and chunk index. Complete frame data is concatenated by chunk index. Frame deadlines order playback. Duplicated packet sequence numbers are ignored.

**What is jitter?** Variation in relative packet transit time. The app smooths differences between sender inter-packet timing and receiver arrival timing. It does not subtract unsynchronized absolute clock readings.

**What does latency mean here?** The dashboard reports TCP round-trip time. The playout buffer adds configured delay. Exact one-way capture-to-display delay is not measured by this implementation.

**Does loss percentage always match the slider?** No. It is random, runs are finite, sequence boundaries are unknown and reorder temporarily resembles loss. Entirely lost prefixes/tails cannot be inferred. A whole JPEG needs all its chunks, so frame loss can exceed packet loss substantially.

**How do multiple receivers affect bandwidth?** This implementation uses unicast fan-out. Source egress is approximately bitrate times receiver count, plus control traffic and headers. It does not use IP multicast.

**What is NS-2 showing?** A simplified UDP/CBR traffic model under propagation delay, error loss and congestion. Its outputs describe the simulation, not a real capture or actual decoded JPEG quality.

**Limitations and future work?** Video only; no audio synchronization, adaptive bitrate, congestion control, retransmission/FEC, encryption, authentication, NAT traversal or relaying. Future extensions could add RTP, synchronized audio, authenticated sessions, quality adaptation and controlled TCP-versus-UDP media experiments.
