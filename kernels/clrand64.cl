#pragma OPENCL EXTENSION cl_khr_int64_base_atomics: enable

// Random number algorithm borrowed from Haskell's random package
// Should somehow replace with Mersenne Twister eventually
typedef int random_state[2];
union random_long {
    random_state r;
    ulong l;
};
inline ulong rand_next(ulong rand_long) {
    union random_long r_union;
    r_union.l = rand_long;
    random_state rand;
    rand[0] = r_union.r[0];
    rand[1] = r_union.r[1];
    int k0 = rand[0] / 53668;
    int s0 = 40014 * (rand[0] % 53668) - k0 * 12211;
    if (s0 < 0) s0 += 2147483563;
    int k1 = rand[1] / 52774;
    int s1 = 40692 * (rand[1] % 52774) - k1 * 3791;
    if (s1 < 0) s1 += 2147483399;
    r_union.r[0] = s0;
    r_union.r[1] = s1;
    return r_union.l;
}
inline float rand_val(ulong rand) {
    union random_long r_union;
    r_union.l = rand;
    long randVal = (long)r_union.r[1] - r_union.r[0];
    randVal += 2147483562;
    randVal %= 2147483562;
    return (float)randVal / 2147483562.f;
}
inline ulong atom_rand(__global volatile ulong *rand) {
    ulong newVal, prevVal;
    do {
        prevVal = *rand;
        newVal = rand_next(prevVal);
    } while (atom_cmpxchg(rand, prevVal, newVal) != prevVal);
    return newVal;
}
inline ulong atom_rand_l(__local volatile ulong *rand) {
    ulong newVal, prevVal;
    do {
        prevVal = *rand;
        newVal = rand_next(prevVal);
    } while (atom_cmpxchg(rand, prevVal, newVal) != prevVal);
    return newVal;
}
// Split global rand with a second stream which can generate random numbers
// in parallel
// Warning: according to Haskell source, no statistical foundation for this
inline ulong2 split_rand(ulong rand) {
    ulong2 splitVal;
    union random_long ru;
    ru.l = rand;
    int s1 = ru.r[0];
    int s2 = ru.r[1];
    ru.l = rand_next(rand);
    int t1 = ru.r[0];
    // Update rand with (new_s1, t2)
    ru.r[0] = (s1 == 2147483562) ? 1 : s1 + 1;
    // Create a second stream (t1, new_s2)
    splitVal.s0 = ru.l;
    ru.r[0] = t1;
    ru.r[1] = (s2 == 1) ? 2147483398 : s2 - 1;
    splitVal.s1 = ru.l;
    return splitVal;
}
    
inline ulong atom_split_rand(__global volatile ulong *rand) {
    ulong newVal, prevVal, retVal;
    do {
        prevVal = *rand;
        ulong2 splitVal = split_rand(prevVal);
        newVal = splitVal.s0;
        retVal = splitVal.s1;
    } while (atom_cmpxchg(rand, prevVal, newVal) != prevVal);
    return retVal;
}
