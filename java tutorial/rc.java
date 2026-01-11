
import java.util.Arrays;

public class rc {
    public static void main(String[] args) {
      
        int[] [] arr={
            {10,20,30};
            {66,44,23};
            {89,60,26};
        }
        System.out.println(Arrays.toString(search(arr,44)));
    }

    static int[] search(int[][] matrix,int target){
       
        int r=0;
        int c=matrix.length-1;
        while(r<matrix[r][c] && c>=0){
            if(matrix[r][c] == target){

                return new int[]{r,c};
            }
        
        if (matrix[r][c]< target){
        r++;
    }else{
        c--;
    }

}
return new int[]{-1,-1};
    }
}

