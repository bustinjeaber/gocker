import os
import sys
import ctypes
import socket

libc = ctypes.CDLL(None)

class Container:
    def __init__(self, rootfs_path, command):
        self.rootfs_path = rootfs_path
        self.command = command

    def start(self):
        print("[gkr] create ner namespace...")
        os.unshare(os.CLONE_NEWPID | os.CLONE_NEWNS | os.CLONE_NEWUTS)
        pid = os.fork()
        if pid == 0:
            try:
                #os.sethostname(b"gocker-env")
                socket.sethostname("gocker")
                os.chroot(self.rootfs_path)
                os.chdir("/")
                libc.mount(b"proc", b"/proc", b"proc", 0, None)
                os.execv(self.command[0], self.command)
            except Exception as e:
                print(f"[gkr] fatal error: {e}")
                sys.exit(1)
        else:
            try:
                _, status = os.waitpid(pid, 0)
                os.system(f"sudo umount -l {self.rootfs_path}/proc 2>/dev/null")
                print(f"\n[gkr] container has been stoped: {status}")
            except KeyboardInterrupt:
                print("\n[gkr] container has been killed")
                os.kill(pid, 9)