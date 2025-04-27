clear;
fprintf('Örnek almak için S, Çýkmak için Q kullanýnýz\n\r');

FilePrefix=input('Dosya Adý:\n','s');
s = serial('COM11');
set(s, 'BaudRate', 115200);
fopen(s);
Sample =0;
RV=''; ReadValue='XXX';
Temperature(1:24,1:32)=0;
finish=0;
StopStream=0;

while ~finish % infinite loop
%     char_input = input('Komut Giriniz S veya Q: ', 's');
     pause(0.1);
     char_input='S';
    if char_input=='S'
        fprintf(s,'%c',char_input);
        
         while ~StopStream 
           RV = fscanf(s,'%s'); 
           if isempty(RV) 
               ReadValue='X';
           else
               ReadValue=RV;
           end
   
           if ReadValue=='X'
               StopStream=0;

           elseif strcmp(ReadValue, 'Start')
             Satir=1;
             Sutun=1;
           elseif strcmp(ReadValue, 'NewLine') 
               Satir=Satir+1;
               Sutun=1; 
           elseif strcmp(ReadValue, 'End') 
                StopStream=1;
           else
                XValue=str2num(ReadValue);
                Temperature(Satir,Sutun)=XValue;
                Sutun=Sutun+1;
         end
        end
   
   
        Filename=strcat(FilePrefix,'_',num2str(Sample),'.txt');
        fprintf('Kayýt Dosya Adý:%s\n',Filename);
        fileID = fopen(Filename,'w');
        for i = 1:24
            for j = 1:32
                fprintf(fileID, '%3.2f ', Temperature(i, j)); 
            end
            fprintf(fileID, '\n');
        end
        fclose(fileID);
        StopStream=0;
        figure(1);
        imshow(Temperature,[20 50],'InitialMagnification', 500);
%         ortalama=mean(Temperature(:))
%         TempDiff = Temperature - ortalama;
%         for (i=1:1:24)
%             for (j=1:1:32) 
%                 if (4<TempDiff<6)  TempEstimated(i,j)=1 
%                 else TempEstimated(i,j)=0;
%                 end
%             end
%         end
        
        
         end
    
    if char_input=='Q'
        finish = 1;
    end
    Sample=Sample+1;
    pause(1);
end 
fclose(s);

clear;




 