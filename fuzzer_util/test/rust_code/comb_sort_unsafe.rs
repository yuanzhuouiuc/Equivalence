mod libc {
    pub use ::libc::*;
}

pub fn sort(numbers: &mut [i32]) {
    let size = numbers.len();
    let mut gap = size;
    let shrink = 2.0;
    
    while gap > 1 {
        gap = (gap as f32 / shrink) as usize;
        let mut i = 0;
        while (i + gap) < size {
            if numbers[i] > numbers[i + gap] {
                let tmp = numbers[i];
                numbers[i] = numbers[i + gap];
                numbers[i + gap] = tmp;
            }
            i += 1;
        }
    }
}

static N: i32 = 97;

pub fn create_array_from_args(args: &[Vec<u8>], size: &mut usize) -> Vec<i32> {
    *size = args.len();
    let mut arr = vec![0; *size];
    
    for (i, arg) in args.iter().enumerate() {
        arr[i] = String::from_utf8_lossy(arg).trim().parse::<i32>().unwrap_or(0);
    }
    
    arr
}

pub fn validate_arg_count(given_argc: &usize, expected_argc: i32) {
    if (*given_argc as i32 - 1) != expected_argc {
        println!("Error: Expected {} arguments, but got {}.", expected_argc, given_argc - 1);
        std::process::exit(1);
    }
}

fn main() {
    let args: Vec<Vec<u8>> = std::env::args_os().map(|x| x.into_vec()).collect();
    
    validate_arg_count(&args.len(), N);
    
    let mut n = N as usize;
    let mut numbers = create_array_from_args(&args[1..], &mut n);
    
    let size = 3;
    
    for _ in 0..size {
        sort(&mut numbers[0..n]);
    }
    
    for num in &numbers[0..n] {
        print!("{} ", num);
    }
    
    println!();
}
