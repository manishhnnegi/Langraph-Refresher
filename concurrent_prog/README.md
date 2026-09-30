# threading
     repo link: https://github.com/codingwithmax/threading-tutorial/tree/main/threading
# asyncronoush
# multiprocessing

########################################################################

When multiple threads, like fn-1 and fn-2, are executed on the same CPU core, they don't literally run at the same time in the strict sense. Instead, they share the CPU core's time through a process called time slicing or context switching.

Time Slicing and Context Switching
Time Slicing: The operating system's scheduler divides the CPU's time into small slices, allocating each thread a brief period to run. This time slice is usually in the order of milliseconds.
Context Switching: When a thread's time slice ends, the operating system saves its current state (context) and switches to another thread. The new thread then starts or resumes execution. This switching happens very quickly, making it appear as though multiple threads are running simultaneously, even on a single core.
Example Execution with fn-1 and fn-2
Starting fn-1:

The operating system gives fn-1 a time slice on the CPU core.
fn-1 begins calculating the sum of squares for n=10,000,000.
It might perform some iterations of the loop and accumulate part of the sum.
Context Switch to fn-2:

After fn-1 has used its time slice, the operating system may decide to switch to fn-2.
The current state of fn-1 (including the value of its variables, current instruction, etc.) is saved.
The CPU core is now allocated to fn-2, which begins calculating the sum of squares for n=20,000,000.
fn-2 performs some iterations of its loop.
Switching Back to fn-1:

After fn-2 uses its time slice, the operating system might switch back to fn-1.
The saved state of fn-1 is restored, and it resumes its calculation right where it left off.
This cycle of switching continues, with both fn-1 and fn-2 getting turns to run on the CPU core.
Parallel-like Execution:

Because the switching happens so fast, usually many thousands of times per second, it creates the illusion that both threads are running simultaneously.
In reality, they are taking turns, but this is done so efficiently that the performance gain is still significant.
Visualization of Time Slicing
Imagine a simplified timeline where each letter represents a small time slice:

plaintext
Copy code
Time --->

CPU Core: | fn-1 | fn-1 | fn-2 | fn-1 | fn-2 | fn-2 | fn-1 | fn-2 | ...

fn-1:       Running             Running             Running         
fn-2:                 Running             Running          Running  
Key Points:
Rapid Switching: The CPU rapidly switches between fn-1 and fn-2, allowing both to make progress almost simultaneously.
Efficient Use of CPU: This method maximizes the use of the CPU core, keeping it busy and reducing idle time.
Illusion of Parallelism: Even on a single core, this rapid switching gives the appearance of parallel execution, which is why threading can be effective even on systems with limited cores.
Conclusion:
Even though fn-1 and fn-2 are technically sharing a single CPU core, they appear to run concurrently because the operating system efficiently manages time slices through context switching. This allows both threads to progress in their calculations without one having to completely finish before the other can start.