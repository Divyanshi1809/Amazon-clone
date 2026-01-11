
import java.util.Arrays;
public class Bubblesort {
    public static void main(String[] args) {
        int[] arr={26,15,13,18,22,1};
        bubble(arr);
        System.out.println(Arrays.toString(arr));
    }

    static void bubble(int[] arr){
        boolean swapped;
        //run steps n-1 time
        for(int i=0;i<arr.length;i++){
            swapped=false;
            // for each steps,max items will come at last respective index
            for(int j=1;j<arr.length-i;j++){
                //swap if item is smaller than previous item
                if(arr[j]<arr[j-1]){
                    //swap
                    int temp=arr[j];
                    arr[j]=arr[j-1];
                    arr[j-1]=temp;
                    swapped=true;
                }
            }
            //if u did not solve for particular i
            if(!swapped){
                break;
            }
        }
    }
}
