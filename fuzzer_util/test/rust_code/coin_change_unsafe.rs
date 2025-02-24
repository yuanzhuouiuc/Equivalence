mod stdio;
mod limits;
mod stdlib;
mod time;

pub fn min_coins(coins: Vec<i32>, m: usize, v: usize) -> i32 {
    let mut table = vec![std::i32::MAX; v + 1];
    table[0] = 0;

    for i in 1..=v {
        for j in 0..m {
            if coins[j] <= i as i32 {
                let sub_res = table[(i - coins[j] as usize) as usize];
                if sub_res != std::i32::MAX && sub_res + 1 < table[i] {
                    table[i] = sub_res + 1;
                }
            }
        }
    }
    table[v]
}

pub fn main() {
    assert!(std::os::args().len() == 98);  // change to std::env::args().len() if you want to run this

    let args: Vec<String> = std::os::args().collect();

    let v: i32 = 98564;
    let mut numbers: Vec<i32> = Vec::new();

    for i in 1..98 {
        numbers.push(args[i].parse::<i32>().unwrap());
    }

    let mut k = 0;
    for _ in 0..5 {
        k = min_coins(numbers.clone(), 97, v as usize);
    }
    println!("{}", k);
}