import av
import numpy as np
import tempfile
import os

print("="*70)
print("COMPREHENSIVE 16-BIT VIDEO ENCODING TEST")
print("PyAV Testing | Multiple Codecs & Pixel Formats")
print("="*70)

# Define test configurations
pixel_formats = [
    'gray16le', 'gray12le', 'gray10le', 
    'rgb48le', 
    'yuv444p16le', 'yuv444p12le', 'yuv444p10le',
    'yuv420p16le', 'yuv420p12le', 'yuv420p10le'
]
codecs = ['libx265', 'libx264', 'libsvtav1', 'ffv1', 'rawvideo']

results = {}

# ============================================================================
# PyAV Testing
# ============================================================================
print("\n" + "="*70)
print("PyAV ENCODING TESTS")
print("="*70)

for codec_name in codecs:
    results[codec_name] = {}
    
    for pix_fmt in pixel_formats:
        print(f"\nPyAV: {codec_name:12s} + {pix_fmt:15s} ", end="")
        
        try:
            # Determine container format
            if codec_name in ['libx265', 'libx264', 'libsvtav1']:
                ext = 'mp4'
            else:
                ext = 'avi'
            
            temp_file = os.path.join(tempfile.gettempdir(), f'pyav_{codec_name}_{pix_fmt}.{ext}')
            
            container = av.open(temp_file, mode='w')
            stream = container.add_stream(codec_name, rate=30)
            stream.width = 640
            stream.height = 480
            stream.pix_fmt = pix_fmt
            
            # Create test frame based on format
            if 'gray' in pix_fmt:
                if '16' in pix_fmt:
                    frame_data = np.random.randint(0, 65536, (480, 640), dtype=np.uint16)
                elif '12' in pix_fmt:
                    frame_data = np.random.randint(0, 4096, (480, 640), dtype=np.uint16)
                elif '10' in pix_fmt:
                    frame_data = np.random.randint(0, 1024, (480, 640), dtype=np.uint16)
                else:
                    frame_data = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
            elif 'rgb48' in pix_fmt:
                frame_data = np.random.randint(0, 65536, (480, 640, 3), dtype=np.uint16)
            elif 'yuv444p' in pix_fmt:
                # YUV444 - full resolution for all planes
                # Use direct plane update method for 10/12-bit, from_ndarray for 16-bit
                if '16' in pix_fmt:
                    y = np.random.randint(0, 65536, (480, 640), dtype=np.uint16)
                    u = np.random.randint(0, 65536, (480, 640), dtype=np.uint16)
                    v = np.random.randint(0, 65536, (480, 640), dtype=np.uint16)
                    frame_data = np.stack([y, u, v], axis=2)
                elif '12' in pix_fmt or '10' in pix_fmt:
                    # Create frame directly and update planes (from_ndarray doesn't support these)
                    frame = av.VideoFrame(640, 480, pix_fmt)
                    
                    if '12' in pix_fmt:
                        frame.planes[0].update(np.random.randint(0, 4096, (480, 640), dtype=np.uint16))
                        frame.planes[1].update(np.random.randint(0, 4096, (480, 640), dtype=np.uint16))
                        frame.planes[2].update(np.random.randint(0, 4096, (480, 640), dtype=np.uint16))
                    else:  # 10-bit
                        frame.planes[0].update(np.random.randint(0, 1024, (480, 640), dtype=np.uint16))
                        frame.planes[1].update(np.random.randint(0, 1024, (480, 640), dtype=np.uint16))
                        frame.planes[2].update(np.random.randint(0, 1024, (480, 640), dtype=np.uint16))
                    
                    # Encode this frame directly
                    for packet in stream.encode(frame):
                        container.mux(packet)
                    
                    for packet in stream.encode():
                        container.mux(packet)
                    
                    container.close()
                    
                    file_size = os.path.getsize(temp_file)
                    print(f"✓ SUCCESS ({file_size:,} bytes)")
                    results[codec_name][pix_fmt] = {'pyav': True, 'pyav_size': file_size}
                    os.remove(temp_file)
                    continue  # Skip the normal frame creation path
            elif 'yuv420p' in pix_fmt:
                # YUV420 - use VideoFrame constructor directly instead of from_ndarray
                # Create frame first, then populate planes
                frame = av.VideoFrame(640, 480, pix_fmt)
                
                if '16' in pix_fmt:
                    frame.planes[0].update(np.random.randint(0, 65536, (480, 640), dtype=np.uint16))
                    frame.planes[1].update(np.random.randint(0, 65536, (240, 320), dtype=np.uint16))
                    frame.planes[2].update(np.random.randint(0, 65536, (240, 320), dtype=np.uint16))
                elif '12' in pix_fmt:
                    frame.planes[0].update(np.random.randint(0, 4096, (480, 640), dtype=np.uint16))
                    frame.planes[1].update(np.random.randint(0, 4096, (240, 320), dtype=np.uint16))
                    frame.planes[2].update(np.random.randint(0, 4096, (240, 320), dtype=np.uint16))
                elif '10' in pix_fmt:
                    frame.planes[0].update(np.random.randint(0, 1024, (480, 640), dtype=np.uint16))
                    frame.planes[1].update(np.random.randint(0, 1024, (240, 320), dtype=np.uint16))
                    frame.planes[2].update(np.random.randint(0, 1024, (240, 320), dtype=np.uint16))
                
                # Encode this frame directly
                for packet in stream.encode(frame):
                    container.mux(packet)
                
                for packet in stream.encode():
                    container.mux(packet)
                
                container.close()
                
                file_size = os.path.getsize(temp_file)
                print(f"✓ SUCCESS ({file_size:,} bytes)")
                results[codec_name][pix_fmt] = {'pyav': True, 'pyav_size': file_size}
                os.remove(temp_file)
                continue  # Skip the normal frame creation path
            
            # Normal frame creation path (for non-yuv420p formats)
            frame = av.VideoFrame.from_ndarray(frame_data, format=pix_fmt)
            
            for packet in stream.encode(frame):
                container.mux(packet)
            
            for packet in stream.encode():
                container.mux(packet)
            
            container.close()
            
            file_size = os.path.getsize(temp_file)
            print(f"✓ SUCCESS ({file_size:,} bytes)")
            results[codec_name][pix_fmt] = {'pyav': True, 'pyav_size': file_size}
            os.remove(temp_file)
            
        except Exception as e:
            error_msg = str(e)[:80]
            print(f"✗ FAILED: {error_msg}")
            results[codec_name][pix_fmt] = {'pyav': False, 'pyav_error': str(e)[:100]}

# ============================================================================
# SUMMARY REPORT
# ============================================================================
print("\n" + "="*70)
print("SUMMARY REPORT")
print("="*70)

print("\nLegend: ✓ = Works | ✗ = Failed")
print("\n" + "-"*70)
print(f"{'Codec':<15} {'Pixel Format':<15} {'Status':<8} {'Size':<15}")
print("-"*70)

for codec_name in codecs:
    for pix_fmt in pixel_formats:
        if codec_name in results and pix_fmt in results[codec_name]:
            res = results[codec_name][pix_fmt]
            status = "✓" if res.get('pyav', False) else "✗"
            size = f"{res.get('pyav_size', 0):,}" if res.get('pyav', False) else "-"
            print(f"{codec_name:<15} {pix_fmt:<15} {status:<8} {size:<15}")

# Print detailed findings
print("\n" + "="*70)
print("KEY FINDINGS")
print("="*70)

print("\n16-bit Format Support:")
for codec_name in codecs:
    formats_16bit = ['gray16le', 'rgb48le', 'yuv444p16le', 'yuv420p16le']
    native_count = 0
    for pix_fmt in formats_16bit:
        if codec_name in results and pix_fmt in results[codec_name]:
            res = results[codec_name][pix_fmt]
            if res.get('pyav', False):
                native_count += 1
    
    if native_count == 4:
        print(f"  {codec_name:15s}: ✓ Full native 16-bit support ({native_count}/4)")
    elif native_count > 0:
        print(f"  {codec_name:15s}: ⚠ Partial support ({native_count}/4 native)")
    else:
        print(f"  {codec_name:15s}: ✗ No 16-bit support")

print("\n12-bit Format Support:")
for codec_name in codecs:
    formats_12bit = ['gray12le', 'yuv444p12le', 'yuv420p12le']
    native_count = 0
    for pix_fmt in formats_12bit:
        if codec_name in results and pix_fmt in results[codec_name]:
            res = results[codec_name][pix_fmt]
            if res.get('pyav', False):
                native_count += 1
    
    if native_count == 3:
        print(f"  {codec_name:15s}: ✓ Full native 12-bit support ({native_count}/3)")
    elif native_count > 0:
        print(f"  {codec_name:15s}: ⚠ Partial support ({native_count}/3 native)")
    else:
        print(f"  {codec_name:15s}: ✗ No 12-bit support")

print("\n10-bit Format Support:")
for codec_name in codecs:
    formats_10bit = ['gray10le', 'yuv444p10le', 'yuv420p10le']
    native_count = 0
    for pix_fmt in formats_10bit:
        if codec_name in results and pix_fmt in results[codec_name]:
            res = results[codec_name][pix_fmt]
            if res.get('pyav', False):
                native_count += 1
    
    if native_count == 3:
        print(f"  {codec_name:15s}: ✓ Full native 10-bit support ({native_count}/3)")
    elif native_count > 0:
        print(f"  {codec_name:15s}: ⚠ Partial support ({native_count}/3 native)")
    else:
        print(f"  {codec_name:15s}: ✗ No 10-bit support")

print("\n" + "="*70)
print("RECOMMENDATIONS")
print("="*70)
print("\nBased on PyAV test results:")
print("  → Check which codecs provide full native support above")
print("  → FFV1 and rawvideo typically best for lossless high bit-depth")
print("  → libx265/libsvtav1 good for compressed 10-12 bit encoding")
print("="*70)
