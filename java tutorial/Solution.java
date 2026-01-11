//find even number of digits

public class Solution {
    public static void main(String[] args) {

        int[] nums={12,45,55,56};
        System.out.println(findNumbers(nums));
        
    }

    static int findNumbers(int[] nums){
        int count=0;
            for(int num:nums){
                if(even(nums)){
                    count++;
                }
            }
        return count;
    }

     static boolean even(int num){
         boolean numberOfDigits = digits(num);


            return numberOfDigits%2==0;
    }

    static boolean digits(int num){
        int count=0;

        while(num>0){
            count++;
            num=num/10;
        }
    }
}
