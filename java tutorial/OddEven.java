public class OddEven {
    public static void main(String[] args) {
       int[] arr={2,2,4,8,8,4,6,7};
       System.out.println(ans(arr));
    }

    private static int ans(int[] arr){
        int unique=0;

        for(int n:arr){
            unique^=n;
        }

        return unique;
    }
}
