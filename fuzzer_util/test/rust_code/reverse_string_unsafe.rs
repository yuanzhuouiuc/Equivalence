mod std;
use std::env;
use std::process;

pub fn reverse(s: &mut [char]) {
    let (mut i, mut j) = (0, s.len() - 1);
    while i < j {
        let c = s[i];
        s[i] = s[j];
        s[j] = c;
        i += 1;
        j -= 1;
    }
}

pub fn create_array_from_args(args: Vec<String>) -> Vec<char> {
    if let Some(arg) = args.into_iter().find(|arg| arg.len() != 1) {
        eprintln!("Error: Argument {} is not a single character.", arg);
        process::exit(1);
    }

    args.iter().map(|arg| arg.chars().next().unwrap()).collect()
}

pub fn validate_arg_count(argc: usize, expected_argc: usize) {
    if argc != expected_argc {
        eprintln!(
            "Error: Expected {} arguments, but got {}.",
            expected_argc, argc
        );
        process::exit(1);
    }
}

pub fn main() {
    let args: Vec<String> = env::args().collect();
    validate_arg_count(args.len() - 1, 306);
    let mut numbers = create_array_from_args(args);
    for _ in 0..11 {
        reverse(&mut numbers);
    }
    for number in &numbers {
        print!("{} ", number);
    }
    println!();
}